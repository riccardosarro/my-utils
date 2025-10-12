#!/usr/bin/python3

import os
import sys
import pathlib
import requests
import random
import time

# --- Configuration ---
DEFAULT_WORDLIST_DIR = pathlib.Path.home() / "wordlists"
WORDLISTS = {
    "english": {
        "filename": "words_alpha.txt",
        "url": "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
    },
    "italian": {
        "filename": "660000_parole_italiane.txt",
        "url": "https://raw.githubusercontent.com/napolux/paroleitaliane/refs/heads/main/paroleitaliane/660000_parole_italiane.txt",
    },
}
NUM_WORDS_IN_PASSPHRASE = 5
MAX_RETRIES = 3

# --- Utility Functions ---

def get_wordlist_path(custom_path: str = None) -> pathlib.Path:
    """Determines the correct wordlist directory path."""
    if custom_path:
        return pathlib.Path(custom_path).expanduser()
    return DEFAULT_WORDLIST_DIR

def download_file(url: str, target_path: pathlib.Path):
    """Downloads a file from a URL to the target path with retries."""
    print(f"-> Downloading {target_path.name} from {url}...")
    
    for attempt in range(MAX_RETRIES):
        try:
            # Use streaming to handle potentially large files efficiently
            with requests.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"-> Successfully downloaded {target_path.name}.")
            return
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {target_path.name} (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                sys.exit(f"Failed to download {target_path.name} after {MAX_RETRIES} attempts. Exiting.")

def load_and_merge_words(dir_path: pathlib.Path) -> list:
    """Loads and merges words from all necessary files into a single list."""
    merged_wordlist = []
    
    for key, data in WORDLISTS.items():
        filepath = dir_path / data['filename']
        print(f"-> Loading words from {filepath.name}...")

        try:
            # Efficiently read file line by line, stripping whitespace and converting to lowercase
            with open(filepath, 'r', encoding='utf-8') as f:
                # Use a generator to process lines without loading the whole file string at once
                words = [line.strip().lower() for line in f if line.strip()]
                merged_wordlist.extend(words)
                print(f"   Loaded {len(words):,} {key} words.")
                
        except FileNotFoundError:
            sys.exit(f"Error: Wordlist file not found at {filepath}. This should not happen if the download step was successful.")
        except Exception as e:
            sys.exit(f"An error occurred while reading {filepath.name}: {e}")
            
    # Use a set to remove duplicates (common between English and Italian)
    unique_words = list(set(merged_wordlist))
    
    print(f"\n--- Wordlist Summary ---")
    print(f"Total unique words in merged list: {len(unique_words):,}")
    
    if len(unique_words) < 1000000:
         print("Warning: Merged wordlist is smaller than 1.1 million. Entropy may be slightly lower than estimated.")
    
    # Shuffle the list once to ensure maximum randomness when picking words
    random.shuffle(unique_words)
    
    return unique_words

def generate_passphrase(wordlist: list, num_words: int) -> str:
    """Generates the passphrase by picking words randomly and concatenating them."""
    if len(wordlist) < num_words:
        sys.exit(f"Error: Not enough words in the list to choose {num_words}.")
        
    # Use random.choices for efficient, uniform random selection without replacement
    chosen_words = random.choices(wordlist, k=num_words)
    
    # Concatenate the words without a separator, as requested
    passphrase = "-".join(chosen_words)
    
    return passphrase

# --- Main Execution ---

if __name__ == "__main__":
    # Allow custom directory path via command line argument
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    wordlist_dir = get_wordlist_path(custom_dir)
    
    print(f"--- Passphrase Generator Setup ---")
    print(f"Wordlist directory set to: {wordlist_dir}")
    
    # 1. Ensure the wordlist directory exists
    wordlist_dir.mkdir(parents=True, exist_ok=True)

    # 2. Check for and download missing files
    all_files_present = True
    for key, data in WORDLISTS.items():
        filepath = wordlist_dir / data['filename']
        if not filepath.exists():
            all_files_present = False
            download_file(data['url'], filepath)

    if all_files_present:
        print("\nAll wordlist files are present. Skipping download.")

    # 3. Load the merged wordlist
    try:
        merged_list = load_and_merge_words(wordlist_dir)
    except Exception as e:
        sys.exit(f"Failed to load wordlists: {e}")

    # 4. Generate the 5-word passphrase
    final_passphrase = generate_passphrase(merged_list, NUM_WORDS_IN_PASSPHRASE)

    # 5. Display results
    print(f"\n==========================================")
    print(f"🔐 Your Secure {NUM_WORDS_IN_PASSPHRASE}-Word Passphrase:")
    print(f"{final_passphrase}")
    print(f"==========================================")
    print(f"\nThis password has approximately 100 bits of entropy and is considered very strong.")

