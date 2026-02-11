import re
import os

# DICTIONARY OF CORRECTIONS - ENHANCED WITH STREET SWAHILI! 🔥
# Marekebisho ya Kiswahili cha Mtaani na cha Kawaida
CORRECTIONS = {
    # === BASIC GRAMMAR FIXES ===
    r'\bMimi nina\b': 'Nina',
    r'\bWewe una\b': 'Una',
    r'\bSisi tuna\b': 'Tuna',
    r'\bWao wana\b': 'Wana',
    r'\bYeye ana\b': 'Ana',
    r'\bMimi ni\b': 'Mimi ni',  # Keep this one
    r'\bHapana\b': 'La',  # More natural
    
    # === SLANG & STREET LANGUAGE ===
    r'\bbaridi\b': 'poa',  # Cool/cold context
    r'\bMsichana baridi\b': 'Demu poa',
    r'\bMvulana baridi\b': 'Kijana poa',
    r'\bHii ni baridi\b': 'Hii ni poa',
    r'\bKufanya mapenzi\b': 'Kulala',  # More polite
    r'\bKuzimu\b': 'Jahannam',
    
    # === COMMON ENGLISH WORDS → SWAHILI SLANG ===
    r'\bShit\b': 'Mavi',
    r'\bFuck\b': 'Shetani',
    r'\bDamn\b': 'Ala',
    r'\bOh my god\b': 'Mungu wangu',
    r'\bOh my God\b': 'Mungu wangu',
    r'\bMy God\b': 'Mungu wangu',
    r'\bJesus\b': 'Yesu',
    r'\bHey\b': 'Oya',
    r'\bHello\b': 'Mambo',
    r'\bHi\b': 'Vipi',
    r'\bBye\b': 'Tutaonana',
    r'\bGoodbye\b': 'Kwaheri',
    r'\bYes\b': 'Ndiyo',
    r'\bNo\b': 'La',
    r'\bOkay\b': 'Sawa',
    r'\bOK\b': 'Sawa',
    r'\bAlright\b': 'Sawa',
    r'\bSure\b': 'Bila shaka',
    r'\bMaybe\b': 'Labda',
    r'\bPlease\b': 'Tafadhali',
    r'\bThank you\b': 'Asante',
    r'\bThanks\b': 'Asante',
    r'\bSorry\b': 'Pole',
    r'\bExcuse me\b': 'Samahani',
    
    # === PEOPLE & RELATIONSHIPS ===
    r'\bDude\b': 'Bro',
    r'\bGuy\b': 'Jamaa',
    r'\bMan\b': 'Bwana',
    r'\bBro\b': 'Kaka',
    r'\bBrother\b': 'Ndugu',
    r'\bSister\b': 'Dada',
    r'\bFriend\b': 'Rafiki',
    r'\bBoss\b': 'Bosi',
    r'\bCop\b': 'Polisi',
    r'\bPolice\b': 'Polisi',
    r'\bDoctor\b': 'Daktari',
    r'\bTeacher\b': 'Mwalimu',
    r'\bKid\b': 'Mtoto',
    r'\bBoy\b': 'Mvulana',
    r'\bGirl\b': 'Msichana',
    r'\bBitch\b': 'Kahaba',  # Harsh but accurate
    r'\bBastard\b': 'Mwizi',
    
    # === ACTIONS & VERBS ===
    r'\bLet\'s go\b': 'Twende',
    r'\bLet us go\b': 'Twende',
    r'\bCome on\b': 'Njoo',
    r'\bHurry up\b': 'Harakisha',
    r'\bWait\b': 'Ngoja',
    r'\bStop\b': 'Simama',
    r'\bRun\b': 'Kimbia',
    r'\bHelp\b': 'Saidia',
    r'\bListen\b': 'Sikiliza',
    r'\bLook\b': 'Angalia',
    r'\bWatch out\b': 'Jihadhari',
    r'\bBe careful\b': 'Kuwa makini',
    r'\bShut up\b': 'Nyamaza',
    
    # === EMOTIONS & EXPRESSIONS ===
    r'\bI love you\b': 'Nakupenda',
    r'\bI hate you\b': 'Ninakuchukia',
    r'\bI\'m sorry\b': 'Samahani',
    r'\bI don\'t know\b': 'Sijui',
    r'\bI don\'t care\b': 'Sijali',
    r'\bI understand\b': 'Naelewa',
    r'\bI\'m scared\b': 'Ninaogopa',
    r'\bI\'m tired\b': 'Nimechoka',
    r'\bI\'m hungry\b': 'Nina njaa',
    r'\bI\'m thirsty\b': 'Nina kiu',
    
    # === QUESTIONS ===
    r'\bWhat\b': 'Nini',
    r'\bWhere\b': 'Wapi',
    r'\bWhen\b': 'Lini',
    r'\bWho\b': 'Nani',
    r'\bWhy\b': 'Kwa nini',
    r'\bHow\b': 'Vipi',
    r'\bWhat\'s happening\b': 'Nini kinaendelea',
    r'\bWhat\'s going on\b': 'Nini inaendelea',
    r'\bWhat the hell\b': 'Nini hii',
    r'\bWhat the fuck\b': 'Nini hii shetani',
    
    # === TIME & PLACE ===
    r'\bNow\b': 'Sasa',
    r'\bLater\b': 'Baadaye',
    r'\bToday\b': 'Leo',
    r'\bTomorrow\b': 'Kesho',
    r'\bYesterday\b': 'Jana',
    r'\bHere\b': 'Hapa',
    r'\bThere\b': 'Pale',
    r'\bEverywhere\b': 'Kila mahali',
    r'\bNowhere\b': 'Mahali popote',
    
    # === COMMON PHRASES ===
    r'\bGood luck\b': 'Bahati njema',
    r'\bGood job\b': 'Kazi nzuri',
    r'\bWell done\b': 'Vizuri sana',
    r'\bNo problem\b': 'Hakuna shida',
    r'\bNo way\b': 'Hapana kabisa',
    r'\bOf course\b': 'Bila shaka',
    r'\bFor sure\b': 'Hakika',
    r'\bI see\b': 'Naona',
    r'\bI got it\b': 'Nimeelewa',
    r'\bNever mind\b': 'Usijali',
    r'\bForget it\b': 'Sahau',
}

def apply_corrections(text):
    """Apply all corrections to a single text string"""
    corrected = text
    
    # Apply all regex corrections
    for mistake, fix in CORRECTIONS.items():
        corrected = re.sub(mistake, fix, corrected, flags=re.IGNORECASE)
    
    # Additional context-aware fixes
    # Capitalize standalone "ndiyo" and "la"
    if corrected.lower().strip() in ["ndiyo", "la", "sawa"]:
        corrected = corrected.capitalize()
    
    # Fix double negatives (common Argos mistake)
    corrected = re.sub(r'\bSi\s+si\b', 'Si', corrected, flags=re.IGNORECASE)
    
    # Remove redundant "mimi" when verb already implies it
    corrected = re.sub(r'\bMimi\s+(nina|nime|nita|nili)\b', r'\1', corrected, flags=re.IGNORECASE)
    
    return corrected

def inspect_and_polish_segments(segments):
    """
    Polish segments in-memory (for use during subtitle generation)
    THE SUPER INSPECTOR - Enhanced with street Swahili! 🔥
    """
    corrections_made = 0
    for seg in segments:
        if 'sw_text' in seg and seg['sw_text']:
            original = seg['sw_text']
            corrected = apply_corrections(original)
            if corrected != original:
                seg['sw_text'] = corrected
                corrections_made += 1
    
    print(f"[✓] Super Inspector: Made {corrections_made} street-level corrections!")
    return segments

def inspect_and_polish(ass_path):
    """
    THE SUPER INSPECTOR (Ukaguzi Maradufu wa Mtaani) 🕵️‍♂️🔥
    
    Final quality check before hardcoding.
    Enhanced with street Swahili and natural language corrections.
    """
    print(f"[*] Super Inspector: Reviewing {os.path.basename(ass_path)}...")
    
    with open(ass_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    corrected_lines = []
    changes_made = 0
    
    for line in lines:
        if line.startswith("Dialogue:"):
            # Extract text part (last field)
            parts = line.split(",,", 1)
            if len(parts) < 2: 
                parts = line.split(",", 9)
                if len(parts) > 9:
                    text_part = parts[-1]
                    meta_part = ",".join(parts[:-1])
                else:
                    corrected_lines.append(line)
                    continue
            else:
                 meta_part = parts[0] + ",,"
                 text_part = parts[1]

            original_text = text_part
            polished_text = apply_corrections(text_part)
            
            if polished_text != original_text:
                changes_made += 1
            
            # Reconstruct
            if len(parts) > 9:
                 corrected_lines.append(f"{meta_part},{polished_text}")
            else:
                 corrected_lines.append(f"{meta_part}{polished_text}")

        else:
            corrected_lines.append(line)
            
    # Save the polished version
    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(corrected_lines)
        
    print(f"[✓] Super Inspector: Approved! Made {changes_made} street-level corrections! 🔥")
    return True
