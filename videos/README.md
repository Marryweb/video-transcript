# Videos Directory

This directory is for storing your video files to be processed by the Video Frames Extraction Service.

## Supported Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WEBM (.webm)
- FLV (.flv)
- WMV (.wmv)
- M4V (.m4v)

## Usage

### Process a single video:
```bash
python -m src.cli.main process videos/your_video.mp4
```

### Process all videos in this directory:
```bash
python -m src.cli.main process videos/ --recursive
```

### Process with custom settings:
```bash
python -m src.cli.main process videos/ --frame-rate 2.0 --max-workers 8
```

## File Organization

You can organize your videos in subdirectories:
```
videos/
├── project1/
│   ├── video1.mp4
│   └── video2.mp4
├── project2/
│   ├── video3.mp4
│   └── video4.mp4
└── standalone_video.mp4
```

The service will process all videos recursively when using the `--recursive` flag.

## Output

Processed results will be saved to the `output/` directory with the following structure:
- `output/frames/` - Extracted frame images
- `output/transcripts/` - Transcript files
- `output/matched/` - Matched frame-transcript data
