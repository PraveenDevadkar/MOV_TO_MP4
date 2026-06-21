import os
import uuid
import threading
import time
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
FILE_TTL = 180  # 3 minutes

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

QUALITY_MAP = {
    'lossless': '0',
    'high':     '18',
    'balanced': '23',
    'small':    '28',
    'tiny':     '35',
}

RESOLUTION_MAP = {
    '1080p': 'scale=-2:1080',
    '720p':  'scale=-2:720',
    '480p':  'scale=-2:480',
}

def delete_after(path, delay=FILE_TTL):
    def _delete():
        time.sleep(delay)
        try:
            os.remove(path)
            print(f'[cleanup] Deleted {path}')
        except FileNotFoundError:
            pass
    threading.Thread(target=_delete, daemon=True).start()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'Empty filename'}), 400

    original_name = secure_filename(f.filename)
    if not original_name.lower().endswith('.mov'):
        return jsonify({'error': 'Only .mov files are accepted'}), 400

    quality    = request.form.get('quality',    'high')
    resolution = request.form.get('resolution', 'original')
    fps        = request.form.get('fps',        'original')

    crf = QUALITY_MAP.get(quality, '18')

    job_id   = uuid.uuid4().hex
    in_path  = os.path.join(UPLOAD_FOLDER, f'{job_id}.mov')
    out_name = original_name.rsplit('.', 1)[0] + '.mp4'
    out_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.mp4')

    f.save(in_path)
    delete_after(in_path)

    cmd = ['ffmpeg', '-y', '-i', in_path]
    cmd += ['-c:v', 'libx264', '-crf', crf, '-preset', 'fast']

    vf_parts = []
    if resolution in RESOLUTION_MAP:
        vf_parts.append(RESOLUTION_MAP[resolution])
    if vf_parts:
        cmd += ['-vf', ','.join(vf_parts)]

    if fps != 'original':
        cmd += ['-r', fps]

    cmd += ['-c:a', 'aac', '-b:a', '192k']
    cmd += ['-movflags', '+faststart']
    cmd.append(out_path)

    print(f'[ffmpeg] Running: {" ".join(cmd)}')

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600
        )
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Conversion timed out'}), 500
    except FileNotFoundError:
        return jsonify({'error': 'FFmpeg not found. Install FFmpeg and add it to PATH.'}), 500

    if result.returncode != 0:
        err = result.stderr.decode('utf-8', errors='replace')[-500:]
        print(f'[ffmpeg] Error:\n{err}')
        return jsonify({'error': f'FFmpeg failed: {err}'}), 500

    delete_after(out_path)

    return send_file(
        out_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=out_name
    )

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
