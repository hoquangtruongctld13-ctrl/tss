#!/usr/bin/env python3
"""
Script to convert CustomTkinter (ctk) widgets to ttkbootstrap (ttk) widgets
Handles the main.py file conversion
"""
import re

def convert_file(input_file, output_file):
    """Convert CustomTkinter widgets to ttkbootstrap in a file"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Conversion mappings
    conversions = [
        # Widget class conversions
        (r'ctk\.CTkFrame\(', 'ttk.Frame('),
        (r'ctk\.CTkLabel\(', 'ttk.Label('),
        (r'ctk\.CTkButton\(', 'ttk.Button('),
        (r'ctk\.CTkEntry\(', 'ttk.Entry('),
        (r'ctk\.CTkTextbox\(', 'ScrolledText('),
        (r'ctk\.CTkComboBox\(', 'ttk.Combobox('),
        (r'ctk\.CTkCheckBox\(', 'ttk.Checkbutton('),
        (r'ctk\.CTkRadioButton\(', 'ttk.Radiobutton('),
        (r'ctk\.CTkSwitch\(', 'ttk.Checkbutton('),
        (r'ctk\.CTkSlider\(', 'ttk.Scale('),
        (r'ctk\.CTkProgressBar\(', 'ttk.Progressbar('),
        (r'ctk\.CTkTabview\(', 'ttk.Notebook('),
        (r'ctk\.CTkScrollableFrame\(', 'ScrolledFrame('),
        (r'ctk\.CTkToplevel\(', 'ttk.Toplevel('),
        
        # Parameter name conversions
        (r'fg_color\s*=', 'bootstyle='),  # Color parameter
        (r'text_color\s*=', 'foreground='),
        (r'corner_radius\s*=\s*\d+,?', ''),  # Remove corner_radius (not in ttk)
        (r'border_width\s*=\s*\d+,?', ''),  # Remove border_width
        (r'hover_color\s*=\s*"[^"]*",?', ''),  # Remove hover_color
        (r'command\s*=\s*lambda:', 'command=lambda event=None:'),  # Fix lambda for ttk
        
        # Icon removals (as requested - no icons on buttons)
        (r'image\s*=\s*[^,\)]+,?\s*', ''),  # Remove image parameter
        (r',\s*compound\s*=\s*"[^"]*"', ''),  # Remove compound parameter
        
        # Method name conversions
        (r'\.configure\(state="disabled"\)', '.configure(state=DISABLED)'),
        (r'\.configure\(state="normal"\)', '.configure(state=NORMAL)'),
        (r'\.configure\(state="readonly"\)', '.configure(state="readonly")'),
        
        # StringVar and IntVar fixes for ttk
        (r'ctk\.StringVar\(', 'tk.StringVar('),
        (r'ctk\.IntVar\(', 'tk.IntVar('),
        (r'ctk\.DoubleVar\(', 'tk.DoubleVar('),
        (r'ctk\.BooleanVar\(', 'tk.BooleanVar('),
    ]
    
    # Apply all conversions
    for pattern, replacement in conversions:
        content = re.sub(pattern, replacement, content)
    
    # Special handling for Tabview -> Notebook conversion
    # tabview.add("Tab Name") → notebook.add(frame, text="Tab Name")
    # This needs manual fixing, so we'll just add a comment
    content = content.replace(
        'self.tabview = ttk.Notebook(',
        '# NOTE: Manual conversion needed for tab creation\nself.tabview = ttk.Notebook('
    )
    
    # Write converted content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Conversion complete! Output written to {output_file}")
    print("\nPlease review the following:")
    print("1. Check all widget parameter conversions")
    print("2. Manually convert tabview.add() to notebook.add(frame, text=...)")
    print("3. Test all functionality")

if __name__ == "__main__":
    convert_file("main.py", "main_converted.py")
