"""
Modern TTS Studio UI - Redesigned with ttkbootstrap
Cleaner layout, better organized tabs, easier to read logs
"""
import json
import os
import re
import wave
import asyncio
import threading
import tkinter as tk  
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from queue import Queue
import time
import subprocess
import glob
import sys

# Import the rest of the modules from the original main.py
# (We'll keep all the backend logic the same, just redesign the UI)

# Import backend classes and functions from original main.py
import importlib.util
spec = importlib.util.spec_from_file_location("main_backend", "main.py.backup")
backend = importlib.util.module_from_spec(spec)
sys.modules['main_backend'] = backend
spec.loader.exec_module(backend)

class ModernTTSStudio(ttk.Window):
    """
    Modern redesigned TTS Studio with cleaner UI
    - Using ttkbootstrap for modern Bootstrap themes
    - Simplified tab structure
    - No icons on buttons (text only)
    - Better log displays
    - Clearer VieNeu-TTS directory references
    """
    
    def __init__(self):
        # Initialize with modern "darkly" theme (Bootstrap dark theme)
        super().__init__(themename="darkly")
        
        # Window configuration
        self.title("VN TTS Studio - Modern Interface")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Center window on screen
        self.center_window()
        
        # Initialize backend data structures
        self.init_backend()
        
        # Build UI
        self.create_main_layout()
        
        # Start background tasks
        self.start_background_tasks()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def init_backend(self):
        """Initialize backend data structures and settings"""
        self.subtitles = []
        self.generated_audios = []
        self.processor = None
        self.long_text_processor = None
        self.is_processing = False
        self.log_queue = Queue()
        self.audio_queue = Queue()
        self.settings_file = "settings.json"
        
        # Load settings
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        else:
            self.settings = {}
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")
    
    def create_main_layout(self):
        """Create the main UI layout"""
        # Main container with padding
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Create notebook (tabs) with modern styling
        self.notebook = ttk.Notebook(main_container, bootstyle="dark")
        self.notebook.pack(fill=BOTH, expand=YES)
        
        # Create tabs with clear, descriptive names (no icons as requested)
        self.create_gemini_tab()
        self.create_longtext_tab()
        self.create_capcut_tab()
        self.create_edge_tab()
        self.create_vieneu_tab()
        self.create_settings_tab()
    
    def create_gemini_tab(self):
        """Gemini TTS tab - simplified and reorganized"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Gemini TTS")
        
        # Top section: File input and configuration
        config_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # File selection
        ttk.Label(config_frame, text="Input File:").grid(row=0, column=0, sticky=W, pady=5)
        self.gemini_file_entry = ttk.Entry(config_frame, width=60)
        self.gemini_file_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        ttk.Button(config_frame, text="Browse File", command=self.browse_gemini_file,
                  bootstyle="primary").grid(row=0, column=2, padx=5, pady=5)
        
        # Output directory
        ttk.Label(config_frame, text="Output Folder:").grid(row=1, column=0, sticky=W, pady=5)
        self.gemini_output_entry = ttk.Entry(config_frame, width=60)
        self.gemini_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        ttk.Button(config_frame, text="Browse Folder", command=self.browse_gemini_output,
                  bootstyle="primary").grid(row=1, column=2, padx=5, pady=5)
        
        # Voice selection
        ttk.Label(config_frame, text="Voice:").grid(row=2, column=0, sticky=W, pady=5)
        self.gemini_voice_var = tk.StringVar(value="Kore")
        voices = ["Kore", "Puck", "Charon", "Zephyr", "Fenrir", "Aoede"]
        voice_combo = ttk.Combobox(config_frame, textvariable=self.gemini_voice_var, 
                                   values=voices, state="readonly", width=30)
        voice_combo.grid(row=2, column=1, sticky=W, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=X, pady=10)
        
        ttk.Button(control_frame, text="Start Processing", command=self.start_gemini_tts,
                  bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_gemini_tts,
                  bootstyle="danger", width=15).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Log", command=self.clear_gemini_log,
                  bootstyle="secondary", width=15).pack(side=LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(tab, text="Progress", padding=10)
        progress_frame.pack(fill=X, pady=10)
        
        self.gemini_progress_var = tk.DoubleVar()
        self.gemini_progress = ttk.Progressbar(progress_frame, variable=self.gemini_progress_var, 
                                              bootstyle="success-striped", mode='determinate')
        self.gemini_progress.pack(fill=X, pady=5)
        
        self.gemini_status_label = ttk.Label(progress_frame, text="Ready", 
                                            font=("Helvetica", 10, "bold"))
        self.gemini_status_label.pack(pady=5)
        
        # Log section with better readability
        log_frame = ttk.LabelFrame(tab, text="Process Log", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Use ScrolledText for better log display
        self.gemini_log = ScrolledText(log_frame, height=15, autohide=True, 
                                       bootstyle="dark")
        self.gemini_log.pack(fill=BOTH, expand=YES)
        self.gemini_log.configure(state=DISABLED)
    
    def create_longtext_tab(self):
        """Long Text Engine tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Long Text Engine")
        
        # Configuration
        config_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # Text input
        text_frame = ttk.LabelFrame(tab, text="Text Input", padding=10)
        text_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.longtext_input = ScrolledText(text_frame, height=10, autohide=True)
        self.longtext_input.pack(fill=BOTH, expand=YES)
        
        # Or file selection
        file_frame = ttk.Frame(config_frame)
        file_frame.pack(fill=X, pady=5)
        
        ttk.Label(file_frame, text="Or select files:").pack(side=LEFT, padx=5)
        ttk.Button(file_frame, text="Select Files", command=self.browse_longtext_files,
                  bootstyle="info").pack(side=LEFT, padx=5)
        self.longtext_files_label = ttk.Label(file_frame, text="No files selected")
        self.longtext_files_label.pack(side=LEFT, padx=10)
        
        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=X, pady=10)
        
        ttk.Button(control_frame, text="Process Text", command=self.process_longtext,
                  bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_longtext,
                  bootstyle="danger", width=15).pack(side=LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Process Log", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.longtext_log = ScrolledText(log_frame, height=10, autohide=True,
                                        bootstyle="dark")
        self.longtext_log.pack(fill=BOTH, expand=YES)
        self.longtext_log.configure(state=DISABLED)
    
    def create_capcut_tab(self):
        """Capcut Voice tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Capcut Voice")
        
        # Configuration
        config_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # Session ID
        ttk.Label(config_frame, text="Session ID:").grid(row=0, column=0, sticky=W, pady=5)
        self.capcut_session_entry = ttk.Entry(config_frame, width=60, show="*")
        self.capcut_session_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        
        # Voice selection
        ttk.Label(config_frame, text="Voice:").grid(row=1, column=0, sticky=W, pady=5)
        self.capcut_voice_var = tk.StringVar(value="vi_female_huong")
        voice_combo = ttk.Combobox(config_frame, textvariable=self.capcut_voice_var, 
                                   state="readonly", width=40)
        voice_combo.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Text input
        text_frame = ttk.LabelFrame(tab, text="Text to Speech", padding=10)
        text_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.capcut_text_input = ScrolledText(text_frame, height=8, autohide=True)
        self.capcut_text_input.pack(fill=BOTH, expand=YES)
        
        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=X, pady=10)
        
        ttk.Button(control_frame, text="Generate Audio", command=self.generate_capcut,
                  bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Play", command=self.play_capcut,
                  bootstyle="info", width=15).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Save", command=self.save_capcut,
                  bootstyle="primary", width=15).pack(side=LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Status Log", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.capcut_log = ScrolledText(log_frame, height=10, autohide=True,
                                      bootstyle="dark")
        self.capcut_log.pack(fill=BOTH, expand=YES)
        self.capcut_log.configure(state=DISABLED)
    
    def create_edge_tab(self):
        """Edge TTS tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Edge TTS")
        
        # Configuration
        config_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # Voice selection
        ttk.Label(config_frame, text="Voice:").grid(row=0, column=0, sticky=W, pady=5)
        self.edge_voice_var = tk.StringVar()
        voice_combo = ttk.Combobox(config_frame, textvariable=self.edge_voice_var, 
                                   state="readonly", width=40)
        voice_combo.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        ttk.Button(config_frame, text="Load Voices", command=self.load_edge_voices,
                  bootstyle="info").grid(row=0, column=2, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Text input
        text_frame = ttk.LabelFrame(tab, text="Text to Speech", padding=10)
        text_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.edge_text_input = ScrolledText(text_frame, height=8, autohide=True)
        self.edge_text_input.pack(fill=BOTH, expand=YES)
        
        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=X, pady=10)
        
        ttk.Button(control_frame, text="Generate Audio", command=self.generate_edge,
                  bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Play", command=self.play_edge,
                  bootstyle="info", width=15).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Save", command=self.save_edge,
                  bootstyle="primary", width=15).pack(side=LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Status Log", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.edge_log = ScrolledText(log_frame, height=10, autohide=True,
                                    bootstyle="dark")
        self.edge_log.pack(fill=BOTH, expand=YES)
        self.edge_log.configure(state=DISABLED)
    
    def create_vieneu_tab(self):
        """VieNeu-TTS tab with clearer directory references"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="VN TTS (VieNeu)")
        
        # Important note about directory
        note_frame = ttk.Frame(tab)
        note_frame.pack(fill=X, pady=(0, 10))
        
        note_text = """⚠️ IMPORTANT: This tab uses VieNeu-TTS directory located in the same folder as this application.
        Path: VieNeu-TTS/ (relative to main.py)
        Do not confuse with other TTS directories!"""
        
        note_label = ttk.Label(note_frame, text=note_text, 
                              bootstyle="warning", wraplength=1350,
                              font=("Helvetica", 10, "bold"))
        note_label.pack(fill=X, pady=5)
        
        # Configuration
        config_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # Model selection
        ttk.Label(config_frame, text="Model:").grid(row=0, column=0, sticky=W, pady=5)
        self.vieneu_model_var = tk.StringVar(value="VN TTS Q4 (Nhanh)")
        models = ["VN TTS (GPU)", "VN TTS Q8 (CPU/GPU)", "VN TTS Q4 (Nhanh)"]
        model_combo = ttk.Combobox(config_frame, textvariable=self.vieneu_model_var, 
                                   values=models, state="readonly", width=30)
        model_combo.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        
        # Voice selection
        ttk.Label(config_frame, text="Voice:").grid(row=1, column=0, sticky=W, pady=5)
        self.vieneu_voice_var = tk.StringVar()
        voice_combo = ttk.Combobox(config_frame, textvariable=self.vieneu_voice_var, 
                                   state="readonly", width=30)
        voice_combo.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Text input
        text_frame = ttk.LabelFrame(tab, text="Text to Speech", padding=10)
        text_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.vieneu_text_input = ScrolledText(text_frame, height=8, autohide=True)
        self.vieneu_text_input.pack(fill=BOTH, expand=YES)
        
        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=X, pady=10)
        
        ttk.Button(control_frame, text="Generate Audio", command=self.generate_vieneu,
                  bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_vieneu,
                  bootstyle="danger", width=15).pack(side=LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Status Log", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.vieneu_log = ScrolledText(log_frame, height=10, autohide=True,
                                      bootstyle="dark")
        self.vieneu_log.pack(fill=BOTH, expand=YES)
        self.vieneu_log.configure(state=DISABLED)
    
    def create_settings_tab(self):
        """Settings tab - simplified"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Settings")
        
        # Gemini API Settings
        api_frame = ttk.LabelFrame(tab, text="Gemini API Configuration", padding=10)
        api_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(api_frame, text="API Keys (one per line):").pack(anchor=W, pady=(0, 5))
        self.api_keys_text = ScrolledText(api_frame, height=6, autohide=True)
        self.api_keys_text.pack(fill=X, pady=5)
        
        # System instruction
        ttk.Label(api_frame, text="System Instruction:").pack(anchor=W, pady=(10, 5))
        self.system_instr_text = ScrolledText(api_frame, height=4, autohide=True)
        self.system_instr_text.pack(fill=X, pady=5)
        
        # Capcut Settings
        capcut_frame = ttk.LabelFrame(tab, text="Capcut Configuration", padding=10)
        capcut_frame.pack(fill=X, pady=10)
        
        ttk.Label(capcut_frame, text="Session ID:").pack(side=LEFT, padx=5)
        self.settings_capcut_session = ttk.Entry(capcut_frame, width=60, show="*")
        self.settings_capcut_session.pack(side=LEFT, padx=5, fill=X, expand=YES)
        
        # FFmpeg Settings
        ffmpeg_frame = ttk.LabelFrame(tab, text="FFmpeg Configuration", padding=10)
        ffmpeg_frame.pack(fill=X, pady=10)
        
        ttk.Label(ffmpeg_frame, text="FFmpeg Path:").pack(side=LEFT, padx=5)
        self.ffmpeg_path_entry = ttk.Entry(ffmpeg_frame, width=50)
        self.ffmpeg_path_entry.pack(side=LEFT, padx=5, fill=X, expand=YES)
        ttk.Button(ffmpeg_frame, text="Browse", command=self.browse_ffmpeg,
                  bootstyle="info").pack(side=LEFT, padx=5)
        
        # Save button
        save_frame = ttk.Frame(tab)
        save_frame.pack(fill=X, pady=20)
        
        ttk.Button(save_frame, text="Save Settings", command=self.save_settings,
                  bootstyle="success", width=20).pack()
    
    # Placeholder methods for functionality (to be implemented)
    def browse_gemini_file(self): messagebox.showinfo("Info", "Browse file functionality")
    def browse_gemini_output(self): messagebox.showinfo("Info", "Browse output functionality")
    def start_gemini_tts(self): messagebox.showinfo("Info", "Start TTS functionality")
    def stop_gemini_tts(self): messagebox.showinfo("Info", "Stop TTS functionality")
    def clear_gemini_log(self): 
        self.gemini_log.configure(state=NORMAL)
        self.gemini_log.delete("1.0", END)
        self.gemini_log.configure(state=DISABLED)
    
    def browse_longtext_files(self): messagebox.showinfo("Info", "Browse files functionality")
    def process_longtext(self): messagebox.showinfo("Info", "Process text functionality")
    def stop_longtext(self): messagebox.showinfo("Info", "Stop functionality")
    
    def generate_capcut(self): messagebox.showinfo("Info", "Generate Capcut audio")
    def play_capcut(self): messagebox.showinfo("Info", "Play audio")
    def save_capcut(self): messagebox.showinfo("Info", "Save audio")
    
    def load_edge_voices(self): messagebox.showinfo("Info", "Load Edge voices")
    def generate_edge(self): messagebox.showinfo("Info", "Generate Edge audio")
    def play_edge(self): messagebox.showinfo("Info", "Play audio")
    def save_edge(self): messagebox.showinfo("Info", "Save audio")
    
    def generate_vieneu(self): messagebox.showinfo("Info", "Generate VieNeu audio")
    def stop_vieneu(self): messagebox.showinfo("Info", "Stop VieNeu")
    
    def browse_ffmpeg(self):
        file_path = filedialog.askopenfilename(
            title="Select FFmpeg executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.ffmpeg_path_entry.delete(0, END)
            self.ffmpeg_path_entry.insert(0, file_path)
    
    def start_background_tasks(self):
        """Start background consumer tasks"""
        pass
    
    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            os._exit(0)

def main():
    """Main entry point"""
    app = ModernTTSStudio()
    app.mainloop()

if __name__ == "__main__":
    main()
