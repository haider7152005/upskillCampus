# FileOrganizer_Haider_USC_UCT.py
# GUI File Organizer using Tkinter
# Author: Haider Ali

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

EXTENSION_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Code": [".py", ".java", ".c", ".cpp", ".js", ".html", ".css", ".ipynb"],
    "Executables": [".exe", ".msi", ".bat", ".sh"],
    "Others": []
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def categorize_file(filename):
    _, ext = os.path.splitext(filename.lower())
    for folder, ext_list in EXTENSION_MAP.items():
        if ext in ext_list:
            return folder
    return "Others"

def organize_folder(target_folder, dry_run=False, on_progress=None):
    planned_moves = []
    for root, _, files in os.walk(target_folder):
        if root != target_folder and any(root.endswith(os.sep + k) for k in EXTENSION_MAP.keys()):
            continue
        for f in files:
            source_path = os.path.join(root, f)
            if f.startswith('.'):
                continue
            category = categorize_file(f)
            dest_dir = os.path.join(target_folder, category)
            dest_path = os.path.join(dest_dir, f)
            planned_moves.append((source_path, dest_path))
    if not dry_run:
        for src, dst in planned_moves:
            ensure_dir(os.path.dirname(dst))
            try:
                base, ext = os.path.splitext(dst)
                counter = 1
                final_dst = dst
                while os.path.exists(final_dst):
                    final_dst = f"{base}_dup{counter}{ext}"
                    counter += 1
                shutil.move(src, final_dst)
                if on_progress:
                    on_progress(f"Moved: {src} -> {final_dst}")
            except Exception as e:
                if on_progress:
                    on_progress(f"Error moving {src}: {e}")
    else:
        for src, dst in planned_moves:
            if on_progress:
                on_progress(f"Planned: {src} -> {dst}")
    return planned_moves

class FileOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer - Haider Ali (upskillCampus)")
        self.geometry("720x520")
        self.resizable(False, False)
        self.selected_folder = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        self.create_widgets()

    def create_widgets(self):
        frm_top = ttk.Frame(self, padding=10)
        frm_top.pack(fill=tk.X)
        ttk.Label(frm_top, text="Selected Folder:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frm_top, textvariable=self.selected_folder, width=60).grid(row=0, column=1, padx=6)
        ttk.Button(frm_top, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=6)

        frm_options = ttk.LabelFrame(self, text="Options", padding=10)
        frm_options.pack(fill=tk.X, padx=10, pady=6)
        ttk.Checkbutton(frm_options, text="Dry Run (do not move files)", variable=self.dry_run).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(frm_options, text="Run Organizer", command=self.run_organizer).grid(row=0, column=1, padx=6)
        ttk.Button(frm_options, text="Refresh Mapping", command=self.show_mapping).grid(row=0, column=2)

        frm_mapping = ttk.LabelFrame(self, text="Extension Mapping", padding=10)
        frm_mapping.pack(fill=tk.BOTH, padx=10, pady=6, expand=True)
        self.txt_mapping = tk.Text(frm_mapping, height=6, wrap=tk.WORD)
        self.txt_mapping.pack(fill=tk.BOTH, expand=True)
        self.show_mapping()

        frm_log = ttk.LabelFrame(self, text="Activity Log", padding=10)
        frm_log.pack(fill=tk.BOTH, padx=10, pady=6, expand=True)
        self.txt_log = tk.Text(frm_log, height=10, wrap=tk.WORD)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        frm_controls = ttk.Frame(self, padding=10)
        frm_controls.pack(fill=tk.X)
        ttk.Button(frm_controls, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=6)
        ttk.Button(frm_controls, text="Open Folder", command=self.open_folder).pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder to organize")
        if folder:
            self.selected_folder.set(folder)
            self.log(f"Selected folder: {folder}")

    def show_mapping(self):
        self.txt_mapping.delete("1.0", tk.END)
        for k, v in EXTENSION_MAP.items():
            self.txt_mapping.insert(tk.END, f"{k}: {', '.join(v) if v else 'Any other extension'}\\n")

    def log(self, message):
        self.txt_log.insert(tk.END, message + "\\n")
        self.txt_log.see(tk.END)

    def clear_log(self):
        self.txt_log.delete("1.0", tk.END)

    def open_folder(self):
        folder = self.selected_folder.get()
        if folder and os.path.exists(folder):
            try:
                if os.name == "nt":
                    os.startfile(folder)
                elif os.name == "posix":
                    import subprocess
                    subprocess.Popen(["xdg-open", folder])
            except Exception as e:
                messagebox.showerror("Open Folder", f"Cannot open folder: {e}")
        else:
            messagebox.showwarning("Open Folder", "No folder selected or folder does not exist.")

    def on_progress(self, message):
        self.log(message)
        self.update_idletasks()

    def run_organizer(self):
        folder = self.selected_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Folder missing", "Please select a valid folder to organize.")
            return
        self.log("Starting organizer...")
        planned = organize_folder(folder, dry_run=self.dry_run.get(), on_progress=self.on_progress)
        if self.dry_run.get():
            messagebox.showinfo("Dry Run Complete", f"Planned {len(planned)} moves. No files were moved (dry run).")
        else:
            messagebox.showinfo("Organizer Complete", f"Organizer moved {len(planned)} files.")

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
