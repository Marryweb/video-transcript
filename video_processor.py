#!/usr/bin/env python3

import os
import cv2
import json
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from typing import List, Dict, Any
import pytesseract

class VideoProcessor:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_frames(self, video_path: str, frame_rate: float = 1.0) -> List[Dict]:
        print(f"📹 Extracting frames from {video_path}...")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        video_name = Path(video_path).stem
        frames_dir = self.output_dir / "frames" / video_name
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        frames = []
        frame_interval = int(fps / frame_rate)
        frame_count = 0
        extracted_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps
                filename = f"{video_name}_frame_{extracted_count:06d}_{timestamp:.2f}s.jpg"
                filepath = frames_dir / filename
                
                cv2.imwrite(str(filepath), frame)
                
                frames.append({
                    "frame_number": extracted_count,
                    "timestamp": timestamp,
                    "filename": filename,
                    "filepath": str(filepath)
                })
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        print(f"✅ Extracted {extracted_count} frames")
        return frames
    
    def transcribe_video(self, video_path: str) -> List[Dict]:
        print(f"🎤 Transcribing {video_path}...")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_path = temp_audio.name
        
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '2',
                '-y', audio_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language="en"
                )
            
            segments = []
            if hasattr(transcript, 'segments'):
                for segment in transcript.segments:
                    segments.append({
                        "start_time": segment.start,
                        "end_time": segment.end,
                        "text": segment.text,
                        "confidence": getattr(segment, 'avg_logprob', 0)
                    })
            else:
                segments.append({
                    "start_time": 0.0,
                    "end_time": 10.0,
                    "text": transcript.text,
                    "confidence": 0.0
                })
            
            print(f"✅ Transcribed {len(segments)} segments")
            return segments
            
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
    
    def extract_text_from_frames(self, frames: List[Dict]) -> List[Dict]:
        """Extract text from frames using OCR"""
        text_segments = []
        for frame in frames:
            try:
                image = cv2.imread(frame["filepath"])
                if image is None:
                    continue
                text = pytesseract.image_to_string(image, config='--psm 6').strip()
                if text and len(text) > 3:
                    text_segments.append({
                        "start_time": frame["timestamp"],
                        "end_time": frame["timestamp"] + 1.0,
                        "text": text,
                        "confidence": 0.8
                    })
            except:
                continue
        return text_segments
    
    def match_frames_with_transcript(self, frames: List[Dict], transcript: List[Dict]) -> List[Dict]:
        print("🔗 Matching frames with transcript...")
        
        matched = []
        for frame in frames:
            frame_time = frame["timestamp"]
            
            matching_segment = None
            for segment in transcript:
                if segment["start_time"] <= frame_time <= segment["end_time"]:
                    matching_segment = segment
                    break
            
            if not matching_segment:
                closest_segment = min(transcript, 
                                    key=lambda s: min(abs(s["start_time"] - frame_time), 
                                                    abs(s["end_time"] - frame_time)))
                matching_segment = closest_segment
            
            matched.append({
                "frame": frame,
                "transcript": matching_segment,
                "match_confidence": 1.0 if matching_segment else 0.0
            })
        
        print(f"✅ Matched {len(matched)} frames")
        return matched
    
    def save_results(self, video_name: str, frames: List[Dict], transcript: List[Dict], matched: List[Dict]):
        print("💾 Saving results...")
        
        frames_file = self.output_dir / "frames" / f"{video_name}_frames.json"
        with open(frames_file, 'w') as f:
            json.dump(frames, f, indent=2)
        
        transcript_file = self.output_dir / "transcript" / f"{video_name}_transcript.json"
        transcript_file.parent.mkdir(exist_ok=True)
        with open(transcript_file, 'w') as f:
            json.dump(transcript, f, indent=2)
        
        matched_file = self.output_dir / "matched" / f"{video_name}_matched.json"
        matched_file.parent.mkdir(exist_ok=True)
        with open(matched_file, 'w') as f:
            json.dump(matched, f, indent=2)
        
        print(f"✅ Results saved to output/")
    
    def process_video(self, video_path: str) -> Dict[str, Any]:
        print(f"\n🎬 Processing: {video_path}")
        print("=" * 50)
        
        video_name = Path(video_path).stem
        
        frames = self.extract_frames(video_path)
        transcript = self.transcribe_video(video_path)
        
        # If audio transcription is poor, try OCR
        if len(transcript) <= 1:
            print("⚠️  Audio transcription seems poor, trying OCR...")
            ocr_text = self.extract_text_from_frames(frames)
            transcript.extend(ocr_text)
        
        matched = self.match_frames_with_transcript(frames, transcript)
        self.save_results(video_name, frames, transcript, matched)
        
        return {
            "video_name": video_name,
            "frames_extracted": len(frames),
            "transcript_segments": len(transcript),
            "matched_pairs": len(matched),
            "status": "success"
        }

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    processor = VideoProcessor(api_key)
    
    videos_dir = Path("videos")
    if not videos_dir.exists():
        print(f"❌ Error: {videos_dir} directory not found")
        return
    
    video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov"))
    
    if not video_files:
        print(f"❌ No video files found in {videos_dir}")
        return
    
    print(f"🎯 Found {len(video_files)} video(s) to process")
    
    results = []
    for video_file in video_files:
        try:
            result = processor.process_video(str(video_file))
            results.append(result)
        except Exception as e:
            print(f"❌ Error processing {video_file}: {e}")
            results.append({
                "video_name": video_file.stem,
                "status": "error",
                "error": str(e)
            })
    
    print("\n" + "=" * 50)
    print("📊 PROCESSING SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    for result in successful:
        print(f"  • {result['video_name']}: {result['frames_extracted']} frames, {result['transcript_segments']} segments")
    
    for result in failed:
        print(f"  • {result['video_name']}: ERROR - {result['error']}")
    
    print(f"\n📁 Results saved in: {processor.output_dir}")
    print("🎉 Processing complete!")

if __name__ == "__main__":
    main()