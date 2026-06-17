from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess, os, uuid, threading, time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Quality presets
QUALITY_PRESETS = {
    "lossless": {"crf": "0",  "preset": "medium", "label": "Lossless"},
    "high":     {"crf": "18", "preset": "slow",   "label": "High"},
    "balanced": {"crf": "23", "preset": "medium", "label": "Balanced"},
    "small":    {"crf": "28", "preset": "fast",   "label": "Small File"},
    "tiny":     {"crf": "35", "preset": "fast",   "label": "Tiny File"},
}

def cleanup_later(paths, delay=180):
    def _run():
        time.sleep(delay)
        for p in paths:
            try:
                if os.path.exists(p): os.remove(p)
            except: pass
    threading.Thread(target=_run, daemon=True).start()

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".mov"):
        return jsonify({"error": "Only .mov files are accepted"}), 400

    quality    = request.form.get("quality", "high")
    resolution = request.form.get("resolution", "original")
    fps        = request.form.get("fps", "original")

    preset_cfg = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["high"])

    uid         = uuid.uuid4().hex
    input_path  = os.path.join(UPLOAD_FOLDER, f"{uid}_in.mov")
    output_path = os.path.join(UPLOAD_FOLDER, f"{uid}_out.mp4")
    file.save(input_path)

    # Build FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", input_path]

    # Video codec — always H.264 for WMP compatibility
    cmd += ["-c:v", "libx264", "-crf", preset_cfg["crf"], "-preset", preset_cfg["preset"]]

    # Resolution scaling
    if resolution == "1080p":
        cmd += ["-vf", "scale=-2:1080"]
    elif resolution == "720p":
        cmd += ["-vf", "scale=-2:720"]
    elif resolution == "480p":
        cmd += ["-vf", "scale=-2:480"]
    else:
        # Keep original but ensure even dimensions (required by H.264)
        cmd += ["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"]

    # FPS
    if fps != "original":
        cmd += ["-r", fps]

    # Audio — always AAC for WMP
    cmd += [
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",  # required for WMP
        output_path
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    except subprocess.CalledProcessError as e:
        cleanup_later([input_path])
        return jsonify({"error": "Conversion failed: " + e.stderr.decode()}), 500
    except subprocess.TimeoutExpired:
        cleanup_later([input_path])
        return jsonify({"error": "Conversion timed out (file too large?)"}), 500

    cleanup_later([input_path, output_path], delay=180)

    out_name = os.path.splitext(file.filename)[0] + ".mp4"
    return send_file(
        output_path,
        as_attachment=True,
        download_name=out_name,
        mimetype="video/mp4"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)