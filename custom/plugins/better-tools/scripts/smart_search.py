import sys
import subprocess
import os

def smart_search(pattern, path="."):
    # Use ripgrep to find matches with context
    # -n: show line numbers
    # -C 5: show 5 lines of context
    # -H: show filenames
    # --heading: group matches by file
    
    cmd = ["rg", "-n", "-C", "5", "--heading", "--color", "never", pattern, path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        elif result.returncode == 1:
            print("No matches found.")
        else:
            print(f"Error running ripgrep: {result.stderr}")
    except FileNotFoundError:
        print("Error: 'rg' (ripgrep) is not installed or not in PATH.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_search.py <pattern> [path]")
        sys.exit(1)
    
    pattern = sys.argv[1]
    target_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    smart_search(pattern, target_path)
