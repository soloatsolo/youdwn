# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        # Load icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
                self.icon_photo = icon_photo  # Keep reference
        except Exception as e:
            print(f"Could not load icon: {e}")

        # Fonts and styles
        self.app_font = ("Helvetica", 11)
        self.title_font = ("Helvetica", 16, "bold")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure colors
        self.style.configure(".", 
            background="#f0f0f0",
            foreground="#333333",
            font=self.app_font
        )
        self.style.configure("Header.TLabel",
            font=self.title_font,
            padding=10
        )
        self.style.configure("URL.TEntry",
            padding=5,
            fieldbackground="white"
        )
        self.style.configure("Download.TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
            background="#4CAF50",
            foreground="white"
        )
        self.style.map("Download.TButton",
            background=[("active", "#45a049"), ("disabled", "#cccccc")],
            foreground=[("disabled", "#666666")]
        )
        
        # Main container with padding
        self.main_frame = ttk.Frame(root, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, 
                 text="YouTube Video Downloader", 
                 style="Header.TLabel").pack()

        # URL Frame
        url_frame = ttk.LabelFrame(self.main_frame, text="Video URL", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = ttk.Entry(url_frame, font=self.app_font, style="URL.TEntry")
        self.url_entry.pack(fill=tk.X, expand=True, pady=5)
        self.url_entry.bind("<Button-3>", self.show_context_menu)
        self.url_entry.bind("<Return>", lambda e: self.get_video_info())
        
        # Video info frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Video Information", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Thumbnail
        self.thumbnail_label = ttk.Label(self.info_frame)
        self.thumbnail_label.pack(pady=5)
        
        # Quality selection
        quality_frame = ttk.Frame(self.info_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        self.quality_combo = ttk.Combobox(quality_frame, state="readonly", font=self.app_font, width=50)
        self.quality_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Audio only option
        self.audio_only = tk.BooleanVar()
        ttk.Checkbutton(quality_frame, 
                       text="Audio Only",
                       variable=self.audio_only,
                       command=self.toggle_audio_only).pack(side=tk.RIGHT)
        
        # Save location frame
        save_frame = ttk.LabelFrame(self.main_frame, text="Save Location", padding=10)
        save_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.save_path = tk.StringVar()
        self.save_entry = ttk.Entry(save_frame, 
                                  textvariable=self.save_path, 
                                  font=self.app_font,
                                  state="readonly")
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(save_frame, 
                  text="Browse",
                  command=self.browse_location).pack(side=tk.RIGHT)
        
        # Download button
        self.download_btn = ttk.Button(self.main_frame,
                                     text="Download",
                                     command=self.start_download,
                                     style="Download.TButton",
                                     state=tk.DISABLED)
        self.download_btn.pack(pady=10)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          variable=self.progress_var,
                                          length=300,
                                          mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame,
                                    text="Ready",
                                    justify=tk.LEFT,
                                    wraplength=700)
        self.status_label.pack(fill=tk.X)
        
        # Context menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.url_entry.event_generate("<<Paste>>"))
        
        # Initialize variables
        self.available_formats = []
        self.video_title = ""
        self.set_default_download_path()

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def set_default_download_path(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads):
            downloads = os.getcwd()
        self.save_path.set(downloads)

    def browse_location(self):
        directory = filedialog.askdirectory(initialdir=self.save_path.get())
        if directory:
            self.save_path.set(directory)

    def get_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Fetching video information...")
        self.progress_var.set(0)
        
        def fetch_info():
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Get thumbnail
                    thumbnail_url = info.get('thumbnail')
                    if thumbnail_url:
                        self.load_thumbnail(thumbnail_url)
                    
                    # Store video title
                    self.video_title = info.get('title', 'video')
                    
                    # Get formats
                    formats = []
                    if self.audio_only.get():
                        formats = [f for f in info['formats'] 
                                 if f.get('vcodec') == 'none']
                    else:
                        formats = [f for f in info['formats']
                                 if f.get('vcodec') != 'none']
                    
                    # Format the quality options
                    self.available_formats = []
                    for f in formats:
                        if self.audio_only.get():
                            label = f"Audio - {f.get('acodec', 'N/A')} - {f.get('abr', 'N/A')}kbps"
                        else:
                            height = f.get('height', 'N/A')
                            fps = f.get('fps', '')
                            vcodec = f.get('vcodec', 'N/A')
                            label = f"{height}p{f' {fps}fps' if fps else ''} - {vcodec}"
                        
                        self.available_formats.append({
                            'label': label,
                            'format_id': f['format_id']
                        })
                    
                    # Update UI
                    self.root.after(0, self.update_ui_after_info)
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))

        threading.Thread(target=fetch_info).start()

    def load_thumbnail(self, url):
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            
            # Resize maintaining aspect ratio
            basewidth = 320
            wpercent = (basewidth / float(image.size[0]))
            hsize = int((float(image.size[1]) * float(wpercent)))
            image = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update thumbnail
            self.root.after(0, lambda: [
                self.thumbnail_label.configure(image=photo),
                setattr(self.thumbnail_label, 'image', photo)
            ])
        except Exception as e:
            print(f"Error loading thumbnail: {e}")

    def update_ui_after_info(self):
        # Update quality combobox
        self.quality_combo['values'] = [f['label'] for f in self.available_formats]
        if self.available_formats:
            self.quality_combo.set(self.available_formats[0]['label'])
            self.download_btn.config(state=tk.NORMAL)
        
        # Update status
        self.status_label.config(text=f"Ready to download: {self.video_title}")

    def toggle_audio_only(self):
        # Re-fetch video info to update format list
        self.get_video_info()

    def start_download(self):
        if not self.available_formats:
            return
            
        selected_index = self.quality_combo.current()
        if selected_index < 0:
            messagebox.showerror("Error", "Please select a quality")
            return
            
        format_id = self.available_formats[selected_index]['format_id']
        
        # Prepare options
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
            'quiet': True
        }
        
        if self.audio_only.get():
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        
        # Disable UI
        self.download_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_label.config(text="Starting download...")
        
        def download_thread():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url_entry.get()])
                self.root.after(0, lambda: [
                    messagebox.showinfo("Success", "Download completed successfully!"),
                    self.status_label.config(text="Download complete"),
                    self.download_btn.config(state=tk.NORMAL)
                ])
            except Exception as e:
                self.root.after(0, lambda: [
                    self.show_error(str(e)),
                    self.download_btn.config(state=tk.NORMAL)
                ])
        
        threading.Thread(target=download_thread).start()

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                # Calculate progress
                total = d.get('total_bytes', 0)
                if not total:
                    total = d.get('total_bytes_estimate', 0)
                
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percentage = (downloaded / total) * 100
                else:
                    percentage = float(d['_percent_str'].replace('%', '').strip())
                
                # Update UI
                self.root.after(0, lambda: [
                    self.progress_var.set(percentage),
                    self.status_label.config(
                        text=f"Downloading: {d['_percent_str']} • "
                             f"Speed: {d.get('_speed_str', 'N/A')} • "
                             f"ETA: {d.get('_eta_str', 'N/A')}"
                    )
                ])
            except Exception as e:
                print(f"Progress error: {e}")
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: [
                self.progress_var.set(100),
                self.status_label.config(text="Processing downloaded file...")
            ])

    def show_error(self, message):
        self.status_label.config(text="Error occurred")
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()