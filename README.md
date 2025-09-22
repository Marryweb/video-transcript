# Video Frame Extractor & Transcriber

A simple Python script that extracts frames from videos and matches them with transcript segments using OpenAI's Whisper API.

## 🚀 Quick Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Add Videos
Place your video files in the `videos/` folder (supports .mp4, .avi, .mov)

### 5. Run Processing
```bash
python video_processor.py
```

### 6. View Results
```bash
python view_results.py
```

### 7. Deactivate Virtual Environment (when done)
```bash
deactivate
```

## 📁 Project Structure

```
sundog/
├── video_processor.py      # Main processing script
├── view_results.py         # Results viewer
├── requirements.txt        # Dependencies
├── README.md              # This file
├── videos/                # Input videos (add your videos here)
└── output/                # Generated results (created after running)
    ├── frames/            # Extracted JPG frames
    ├── transcript/        # Transcript JSON files
    └── matched/           # Frame-transcript pairs
```

## 🎯 What It Does

1. **Extracts frames** from videos at 1 frame per second
2. **Transcribes audio** using OpenAI Whisper API
3. **Matches frames** with corresponding transcript segments
4. **Saves results** in organized JSON files

## 📊 Example Output

### Frame Data
```json
{
  "frame_number": 0,
  "timestamp": 0.0,
  "filename": "video1_frame_000000_0.00s.jpg",
  "filepath": "output/frames/video1/video1_frame_000000_0.00s.jpg"
}
```

### Transcript Data
```json
{
  "start_time": 0.0,
  "end_time": 10.0,
  "text": "Thanks for watching!",
  "confidence": -0.98
}
```

### Matched Data
```json
{
  "frame": { /* frame data */ },
  "transcript": { /* transcript data */ },
  "match_confidence": 1.0
}
```

## 🔧 Requirements

- Python 3.7+
- Virtual environment (recommended for macOS/Linux)
- OpenAI API key
- FFmpeg (for audio extraction)
- Video files in `videos/` folder

**Note:** On macOS and Linux, you may need to use a virtual environment due to externally managed Python environments.

## 📝 Features

- ✅ Extracts frames at 1 FPS
- ✅ Transcribes using OpenAI Whisper
- ✅ Matches frames with transcript segments
- ✅ Saves organized JSON output
- ✅ Simple, readable code
- ✅ Error handling

## 🎬 Supported Video Formats

- MP4
- AVI
- MOV

## 📈 Performance

- Processes ~10-15 second videos in 5-10 seconds
- Extracts frames at ~20 frames/second
- Transcribes audio in 3-5 seconds per video

---

**Simple, clean, and effective!** 🎉
