#!/usr/bin/env python3
import re
import sys

def fix_indentation_errors(file_path):
    print(f"Fixing indentation errors in {file_path}")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern 1: Fix indentation after if context and hasattr blocks with 4 lines inside
    pattern1 = r'(if context and hasattr\(context, \'user_data\'\):)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s*)([^\n]+\n)'
    
    def fix_pattern1(match):
        if_statement = match.group(1)
        indent1 = match.group(2)
        line1 = match.group(3)
        indent2 = match.group(4)
        line2 = match.group(5)
        indent3 = match.group(6)
        line3 = match.group(7)
        indent4 = match.group(8)
        line4 = match.group(9)
        indent5 = match.group(10) if match.group(10) else indent4
        line5 = match.group(11)
        
        # Check if the last line has incorrect indentation (less than the previous lines)
        if len(indent5.strip()) < len(indent4.strip()):
            # Fix the indentation to match the previous lines
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent4}{line4}{indent4}{line5}"
        else:
            # Keep as is if indentation is already correct
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent4}{line4}{indent5}{line5}"
    
    # Pattern 2: Fix indentation after if context and hasattr blocks with 5 lines inside
    pattern2 = r'(if context and hasattr\(context, \'user_data\'\):)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s*)([^\n]+\n)'
    
    def fix_pattern2(match):
        if_statement = match.group(1)
        indent1 = match.group(2)
        line1 = match.group(3)
        indent2 = match.group(4)
        line2 = match.group(5)
        indent3 = match.group(6)
        line3 = match.group(7)
        indent4 = match.group(8)
        line4 = match.group(9)
        indent5 = match.group(10)
        line5 = match.group(11)
        indent6 = match.group(12) if match.group(12) else indent5
        line6 = match.group(13)
        
        # Check if the last line has incorrect indentation (less than the previous lines)
        if len(indent6.strip()) < len(indent5.strip()):
            # Fix the indentation to match the previous lines
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent4}{line4}{indent5}{line5}{indent5}{line6}"
        else:
            # Keep as is if indentation is already correct
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent4}{line4}{indent5}{line5}{indent6}{line6}"
    
    # Pattern 3: Fix indentation after if context and hasattr blocks with 3 lines inside
    pattern3 = r'(if context and hasattr\(context, \'user_data\'\):)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s+)([^\n]+\n)(\s*)([^\n]+\n)'
    
    def fix_pattern3(match):
        if_statement = match.group(1)
        indent1 = match.group(2)
        line1 = match.group(3)
        indent2 = match.group(4)
        line2 = match.group(5)
        indent3 = match.group(6)
        line3 = match.group(7)
        indent4 = match.group(8) if match.group(8) else indent3
        line4 = match.group(9)
        
        # Check if the last line has incorrect indentation (less than the previous lines)
        if len(indent4.strip()) < len(indent3.strip()):
            # Fix the indentation to match the previous lines
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent3}{line4}"
        else:
            # Keep as is if indentation is already correct
            return f"{if_statement}{indent1}{line1}{indent2}{line2}{indent3}{line3}{indent4}{line4}"
    
    # Apply the fixes in sequence
    fixed_content = re.sub(pattern1, fix_pattern1, content)
    fixed_content = re.sub(pattern2, fix_pattern2, fixed_content)
    fixed_content = re.sub(pattern3, fix_pattern3, fixed_content)
    
    # Fix the 'el' markers that might be in the code
    fixed_content = fixed_content.replace('el    ', '    ')
    
    # Line-by-line approach to catch any remaining issues
    lines = fixed_content.splitlines()
    fixed_lines = []
    
    # Track indentation levels
    prev_indent = 0
    in_if_block = False
    
    for i, line in enumerate(lines):
        # Check for if context and hasattr pattern
        if "if context and hasattr(context, 'user_data'):" in line:
            in_if_block = True
            prev_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        elif in_if_block and line.strip() and not line.strip().startswith('#'):
            # Check if this line should be indented
            curr_indent = len(line) - len(line.lstrip())
            
            # If this line is less indented than the previous indented line in the block
            # and it's not a closing line (like 'else:' or a new function)
            if curr_indent <= prev_indent and not line.strip().startswith(('else:', 'elif', 'except:', 'finally:', 'def ', 'async def ', 'class ')):
                # This line should be indented more
                spaces = ' ' * (prev_indent + 4)  # Standard 4-space Python indentation
                fixed_lines.append(spaces + line.lstrip())
                
                # If this was the last line in the if block, reset the flag
                if "context.user_data[" in line:
                    in_if_block = False
            else:
                fixed_lines.append(line)
                
                # Update previous indent if this line is properly indented
                if curr_indent > prev_indent:
                    prev_indent = curr_indent
        else:
            fixed_lines.append(line)
            
            # Reset if block flag if we hit a blank line or comment
            if not line.strip() or line.strip().startswith('#'):
                in_if_block = False
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(fixed_lines))
    
    print(f"Fixed indentation errors in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "trading_bot/main.py"
    
    fix_indentation_errors(file_path) 