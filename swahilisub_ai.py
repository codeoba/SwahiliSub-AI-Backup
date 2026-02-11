#!/usr/bin/env python3
"""
SwahiliSub-AI: KIBABE Swahili Subtitle Generator
WITH GOOGLE TRANSLATE (RELIABLE & FAST!)
"""
import os
import sys
import json
import re
# import whisper (lazy import below)
from googletrans import Translator
import time

# FORCE UTF-8 for Terminal / Printing
if sys.stdout.encoding != 'UTF-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    except:
        pass

def find_ffmpeg():
    """Robust discovery of ffmpeg.exe in common locations"""
    import shutil
    import glob
    
    # 0. Check KNOWN path (Fastest)
    known_path = r"C:\Users\CodeOba\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
    if os.path.exists(known_path):
        return known_path

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
            
    return None

# Add FFmpeg to PATH for Whisper/Subprocesses
FFMPEG_EXE = find_ffmpeg()
if FFMPEG_EXE and FFMPEG_EXE != "ffmpeg":
    ffmpeg_dir = os.path.dirname(FFMPEG_EXE)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.path.pathsep + ffmpeg_dir
        print(f"[*] Added FFmpeg to PATH: {ffmpeg_dir}")

def clean_swahili(text):
    """Remove weird artifacts from translation"""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def polish_grammar(text):
    """Quick grammar fixes"""
    # Remove redundant pronouns
    text = re.sub(r'\bMimi\s+ni\s+', 'Ni ', text, flags=re.IGNORECASE)
    text = re.sub(r'\bWewe\s+ni\s+', 'Ni ', text, flags=re.IGNORECASE)
    return text

# Initialize Google Translate
def setup_translator():
    """Initialize Google Translate"""
    return Translator()

def translate_contextual_blocks(segments, target_lang='sw', json_cache_path=None):
    print("[*] Google Translate Mode: RELIABLE & FAST Translation...")
    
    # Setup Google Translate
    translator = setup_translator()
    
    # 1. Collect all text blocks that need translation
    blocks_to_translate = []
    block_indices = []
    
    for i, seg in enumerate(segments):
        # Skip empty or already processed
        if seg.get('sw_text'): 
            continue
        
        text = seg['text'].strip()
        if not text:
            seg['sw_text'] = ""
            continue
        
        blocks_to_translate.append(text)
        block_indices.append(i)
    
    if not blocks_to_translate:
        print("    - All segments already translated!")
        return segments
    
    # 2. Translate using Google Translate
    print(f"    - Translating {len(blocks_to_translate)} segments with Google Translate...")
    
    for i, idx in enumerate(block_indices):
        text = blocks_to_translate[i]
        try:
            # Translate to Swahili
            result = translator.translate(text, src='en', dest=target_lang)
            translated = result.text
            cleaned = clean_swahili(translated)
            polished = polish_grammar(cleaned)
            
            # Apply translation immediately to segment
            segments[idx]['sw_text'] = polished
            
            if (i+1) % 50 == 0:
                print(f"    - [Google] Translated {i+1}/{len(blocks_to_translate)} segments...")
                # Save checkpoint
                if json_cache_path:
                    with open(json_cache_path, 'w', encoding='utf-8') as f:
                        json.dump(segments, f, ensure_ascii=False, indent=2)
            
            # Rate limiting to avoid blocking
            if (i+1) % 100 == 0:
                time.sleep(1)
                
        except Exception as e:
            print(f"    - [!] Translation error for segment {i}: {e}")
            # Skip this segment translation, will remain available for retry later
            continue
    
    # 4. Final Save
    if json_cache_path:
        with open(json_cache_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        print(f"    - [Checkpoint] All translations saved to {os.path.basename(json_cache_path)}")
    
    return segments

def seconds_to_ass(seconds):
    """Convert seconds to ASS timestamp format (H:MM:SS.CS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

def generate_swahili_subtitles(video_path):
    """
    Main function: Generate Swahili subtitles with ARGOS TRANSLATE
    """
    print(f"\n[*] Processing: {os.path.basename(video_path)}")
    
    # Paths
    base_name = os.path.splitext(video_path)[0]
    json_path = base_name + "_transcription.json"
    output_ass = base_name + "_kiswahili.ass"
    
    # Step 1: Transcription (or load from cache)
    if os.path.exists(json_path):
        print(f"[*] Loading cached transcription: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            segments = json.load(f)
    else:
        print("[*] Transcribing audio with Whisper (base model)...")
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(video_path, language="en", verbose=False)
        segments = result['segments']
        
        # Save cache
        print(f"[*] Saving transcription cache: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
    
    # Filter Silence / Hallucinations
    print("[*] Filtering silence and hallucinations...")
    filtered_segments = []
    for seg in segments:
        # Silence Check
        if seg.get('no_speech_prob', 0) > 0.6:
            continue
        
        text = seg.get('text', '').strip()
        if not text or len(text) < 2:
            continue
        
        # Hallucination patterns
        if any(pattern in text.lower() for pattern in [
            'thank you for watching', 'subscribe', 'like and subscribe',
            'please subscribe', 'don\'t forget to subscribe'
        ]):
            continue
        
        filtered_segments.append(seg)
    
    segments = filtered_segments
    print(f"[*] Kept {len(segments)} valid segments")
    
    # Step 2: Translation with ARGOS TRANSLATE
    print("[*] Translating to Swahili with Argos Translate...")
    segments = translate_contextual_blocks(segments, json_cache_path=json_path)
    
    # Step 3: ASS Generation with Cinema Styles
    header = f"""[Script Info]
Title: SwahiliSub AI Generated
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H0000FFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,20,1
Style: Shout,Arial,26,&H000000FF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,20,1
Style: Whisper,Arial,24,&H00CCCCCC,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,2,1,2,10,10,20,1
Style: Question,Arial,24,&H00FFFF00,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    print(f"[*] Creating refined ASS: {output_ass}")
    
    # CRITICAL VALIDATION: Ensure segments have Swahili translations!
    print("[*] Validating Swahili translations...")
    total_segments = len(segments)
    translated_segments = sum(1 for seg in segments if seg.get('sw_text'))
    
    print(f"    - Total segments: {total_segments}")
    print(f"    - Translated segments: {translated_segments}")
    
    if translated_segments == 0:
        print("[!] ERROR: NO SWAHILI TRANSLATIONS FOUND!")
        print("[!] Cannot create ASS file - translation failed!")
        return None
    
    if translated_segments < total_segments * 0.8:
        print(f"[!] ERROR: Only {translated_segments}/{total_segments} segments translated!")
        print(f"[!] This is less than 80% - translation likely failed!")
        return None
    
    print(f"[+] Validation PASSED: {translated_segments}/{total_segments} segments have Swahili!")
    
    # THE INSPECTOR: Final Quality Check 🕵️‍♂️
    print("[*] The Inspector: Running final quality check...")
    from inspector import inspect_and_polish_segments
    segments = inspect_and_polish_segments(segments)
    
    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(header)
        
        for seg in segments:
            # CRITICAL: ONLY use Swahili text! Skip if no translation!
            if not seg.get('sw_text'):
                continue
            
            text = seg['sw_text'].strip()
            if not text: continue
            
            start = seconds_to_ass(seg['start'])
            end = seconds_to_ass(seg['end'])
            
            # Smart Styling Logic 🧠
            style = "Default"
            if text.endswith("!") or text.isupper():
                style = "Shout" # Red
            elif text.endswith("?"):
                style = "Question" # Cyan
            elif text.startswith("(") or text.startswith("["):
                style = "Whisper" # Grey Italic
            
            f.write(f"Dialogue: 0,{start},{end},{style},,0,0,0,,{text}\n")

    print(f"[*] Successfully created SWAHILI ASS Subtitles: {output_ass}")
   
    if os.path.exists(output_ass) and os.path.getsize(output_ass) > 1000:
        return output_ass
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python swahilisub_ai.py <video_path>")
    else:
        raw_path = sys.argv[1]
        
        # 1. Try directly
        if os.path.exists(raw_path):
            generate_swahili_subtitles(raw_path)
        else:
            # 2. Try to find it if there's an encoding mismatch (KIBABE handling)
            print(f"[*] Path not found directly: {raw_path}")
            print("[*] Attempting robust discovery...")
            
            directory = os.path.dirname(raw_path) or "."
            filename = os.path.basename(raw_path)
            
            # Use glob to find matches in the same directory
            import glob
            # Try to match by ignoring special chars or using basic patterns
            # We'll look for files with similar base names
            search_pattern = os.path.join(directory, "*")
            all_files = glob.glob(search_pattern)
            
            found = False
            for f in all_files:
                # Normalize both for comparison (basic)
                if os.path.basename(f) == filename:
                    print(f"[+] Found match with robust discovery: {f}")
                    generate_swahili_subtitles(f)
                    found = True
                    break
            
            if not found:
                print(f"[!] File halipo (Hata kwa discovery): {raw_path}")
                sys.exit(1)
