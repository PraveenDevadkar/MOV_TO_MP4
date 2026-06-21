# 🎬 MOV → MP4 Converter

A local web app that converts `.mov` files to `.mp4` using Python, Flask, and FFmpeg. Output files are H.264 + AAC encoded — compatible with Windows Media Player, VLC, and every major video player.

---

## ✨ Features

- 🎞️ Drag & drop or click to upload `.mov` files
- ⚙️ Quality control — Lossless / High / Balanced / Small / Tiny (CRF 0–35)
- 📐 Resolution options — Original / 1080p / 720p / 480p
- 🎥 Frame rate options — Original / 60fps / 30fps / 24fps
- 🪟 Windows Media Player compatible output (H.264 + AAC)
- 🗑️ Auto-deletes uploaded and converted files after 3 minutes
- 📱 Mobile friendly, responsive UI

---

## 🛠️ Tech Stack

| Layer    | Technology          |
|----------|---------------------|
| Frontend | HTML, CSS, JS       |
| Backend  | Python, Flask       |
| Video    | FFmpeg (libx264)    |
| CORS     | flask-cors          |

---

## 📦 Requirements

- Python 3.8+
- FFmpeg installed and added to PATH
- pip packages: `flask`, `flask-cors`, `werkzeug`

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/mov-to-mp4-converter.git
cd mov-to-mp4-converter
```

### 2. Install Python dependencies

```bash
pip install flask flask-cors werkzeug
```

### 3. Install FFmpeg

**Windows:**
```bash
winget install ffmpeg
```
Or download from [ffmpeg.org](https://ffmpeg.org/download.html), extract to `C:\ffmpeg`, and add `C:\ffmpeg\bin` to your system PATH.

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 4. Run the app

```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:10000
* Running on http://127.0.0.1:10000
* Running on http://192.168.x.x:10000
```

### 5. Open in browser

```
http://127.0.0.1:10000
```

Or use your local network IP (shown in terminal) to access from other devices on the same network.

---

## 📁 Project Structure

```
mov-to-mp4-converter/
├── app.py          # Flask backend
├── index.html      # Frontend UI
├── uploads/        # Temp folder for uploaded MOV files (auto-created)
├── outputs/        # Temp folder for converted MP4 files (auto-created)
└── README.md
```

---

## ⚙️ Configuration

In `app.py` you can change:

| Variable       | Default | Description                        |
|----------------|---------|------------------------------------|
| `MAX_FILE_SIZE`| 2 GB    | Maximum upload file size           |
| `FILE_TTL`     | 180s    | Seconds before files are deleted   |
| `port`         | 10000   | Port the server runs on            |

---

## 🔒 Privacy

All files are processed **locally on your machine**. Nothing is uploaded to any external server. Uploaded and converted files are automatically deleted from disk after 3 minutes.

---

## 📝 License

MIT License — free to use, modify, and distribute.
