import sys
import os

def atomic_edit(target_file):
    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' does not exist.")
        sys.exit(1)

    # Read all stdin
    try:
        input_data = sys.stdin.read()
    except Exception as e:
        print(f"Error reading stdin: {e}")
        sys.exit(1)

    # Parse STDIN for SEARCH and REPLACE blocks
    # Expected format:
    # <<<<<<< SEARCH
    # [content]
    # =======
    # [content]
    # >>>>>>> REPLACE
    
    try:
        search_marker = "<<<<<<< SEARCH"
        mid_marker = "======="
        replace_marker = ">>>>>>> REPLACE"
        
        search_start = input_data.find(search_marker)
        mid_start = input_data.find(mid_marker)
        replace_end = input_data.find(replace_marker)
        
        if search_start == -1 or mid_start == -1 or replace_end == -1:
            raise ValueError("Input format invalid. Must contain SEARCH, separator, and REPLACE blocks.")
            
        # Extract content between markers
        # We need to handle the newlines carefully.
        # usually markers are on their own lines.
        
        # Helper to strip marker line
        def extract_clean(start, end, data):
            # Find the position after the first newline following start
            # Or if start is the beginning of data
            # This is tricky because the marker might be at the end of line or start of line.
            
            # Simple assumption: The agent sends markers on their own lines.
            
            raw = data[start:end]
            # remove the marker itself from the raw block?
            # No, 'start' is the index of marker start.
            
            pass 

        # Let's slice simply first
        s_block = input_data[search_start + len(search_marker) : mid_start]
        r_block = input_data[mid_start + len(mid_marker) : replace_end]
        
        # Trim leading newline if present (artifact of marker line)
        if s_block.startswith('\r\n'): s_block = s_block[2:]
        elif s_block.startswith('\n'): s_block = s_block[1:]
        
        # Trim trailing newline if present (artifact of marker line being before next marker)
        if s_block.endswith('\r\n'): s_block = s_block[:-2]
        elif s_block.endswith('\n'): s_block = s_block[:-1]
        
        if r_block.startswith('\r\n'): r_block = r_block[2:]
        elif r_block.startswith('\n'): r_block = r_block[1:]
        
        if r_block.endswith('\r\n'): r_block = r_block[:-2]
        elif r_block.endswith('\n'): r_block = r_block[:-1]
        
        find_text = s_block
        replace_text = r_block

    except Exception as e:
        print(f"Error parsing input: {e}")
        sys.exit(1)

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    count = content.count(find_text)
    
    if count == 0:
        # Fallback: try stripping outer whitespace from both
        find_stripped = find_text.strip()
        if content.count(find_stripped) == 1:
            print("Warning: Exact match failed, but stripped match found 1 occurrence. Proceeding with stripped match.")
            # We need to replace the STRIPPED version in content
            # But wait, replace_text might have whitespace we want to keep?
            # If we match stripped, we should probably replace the stripped match.
            
            # But the content in file might have surrounding newlines we don't want to kill if replace_text doesn't have them?
            # Safe logic: just use replace(find_stripped, replace_text.strip()?)
            # No, let's keep replace_text as is.
            
            new_content = content.replace(find_stripped, replace_text) 
            # This might be dangerous if find_stripped matches somewhat vaguely.
            pass
        else:
             print(f"Error: Search block not found in '{target_file}'.")
             print(f"(Expected {len(find_text)} chars)")
             sys.exit(1)
    elif count > 1:
        print(f"Error: Search block found {count} times. Ambiguous edit.")
        sys.exit(1)
    else:
        new_content = content.replace(find_text, replace_text)

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully applied atomic edit to '{target_file}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python atomic_edit.py <target_file>")
        print("Input must be piped via stdin in <<<<<<< SEARCH ... format")
        sys.exit(1)
    
    atomic_edit(sys.argv[1])
