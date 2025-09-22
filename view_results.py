#!/usr/bin/env python3

import json
from pathlib import Path

def view_results():
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("❌ No output directory found. Run video_processor.py first.")
        return
    
    print("📊 VIDEO PROCESSING RESULTS")
    print("=" * 50)
    
    matched_dir = output_dir / "matched"
    if not matched_dir.exists():
        print("❌ No matched results found.")
        return
    
    for matched_file in matched_dir.glob("*.json"):
        video_name = matched_file.stem.replace("_matched", "")
        print(f"\n🎬 {video_name.upper()}")
        print("-" * 30)
        
        try:
            with open(matched_file, 'r') as f:
                matched_data = json.load(f)
            
            print(f"📹 Total frames: {len(matched_data)}")
            
            for i, item in enumerate(matched_data[:5]):
                frame = item["frame"]
                transcript = item["transcript"]
                
                print(f"\n  Frame {frame['frame_number']} ({frame['timestamp']:.1f}s)")
                print(f"  📷 {frame['filename']}")
                print(f"  🎤 \"{transcript['text'].strip()}\"")
                print(f"  ⏱️  {transcript['start_time']:.1f}s - {transcript['end_time']:.1f}s")
            
            if len(matched_data) > 5:
                print(f"\n  ... and {len(matched_data) - 5} more frames")
            
            transcript_file = output_dir / "transcript" / f"{video_name}_transcript.json"
            if transcript_file.exists():
                with open(transcript_file, 'r') as f:
                    transcript_data = json.load(f)
                
                print(f"\n  📝 Transcript Summary:")
                print(f"  Segments: {len(transcript_data)}")
                for segment in transcript_data:
                    print(f"    • {segment['start_time']:.1f}s-{segment['end_time']:.1f}s: \"{segment['text'].strip()}\"")
        
        except Exception as e:
            print(f"❌ Error reading {matched_file}: {e}")
    
    print(f"\n📁 All files saved in: {output_dir}")
    print("🎉 View complete!")

if __name__ == "__main__":
    view_results()