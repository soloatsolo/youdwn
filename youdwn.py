# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader (yt-dlp)")
        self.root.geometry("900x780")  # Increased height further
        self.root.configure(bg="#f0f0f0")
        self.app_font = ("Arial", 12)

        # URL Frame
        url_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        url_frame.pack(fill="x", padx=20)
        self.url_label = tk.Label(url_frame, text="Enter YouTube URL:", bg="#f0f0f0", font=self.app_font)
        self.url_label.pack(side="left", padx=5)
        self.url_entry = tk.Entry(url_frame, font=self.app_font, width=60)
        self.url_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.url_entry.bind("<Button-3>", self.show_context_menu)
        self.url_entry.bind("<Return>", lambda event: self.get_video_info())

        # Get Info Button
        self.info_btn = tk.Button(url_frame, text="Get Info", command=self.get_video_info, font=self.app_font, bg="#2196F3", fg="white", padx=10)
        self.info_btn.pack(side="right", padx=5)


        # Thumbnail Frame
        self.thumbnail_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        self.thumbnail_frame.pack(fill="x", padx=20)
        self.thumbnail_label = tk.Label(self.thumbnail_frame, text="Video Thumbnail", font=self.app_font, bg="#f0f0f0")
        self.thumbnail_label.pack()
        self.image_label = tk.Label(self.thumbnail_frame, bg="#f0f0f0")
        self.image_label.pack(pady=10)

        # Download Options Frame (Restructured)
        options_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        options_frame.pack(fill="x", padx=20)

        # Quality Selection (inside a LabelFrame)
        quality_frame = tk.LabelFrame(options_frame, text="Video Quality", font=self.app_font, bg="#f0f0f0", padx=10, pady=5)
        quality_frame.pack(fill="x")

        self.quality_combo = ttk.Combobox(quality_frame, state="readonly", font=self.app_font, width=50)
        self.quality_combo.pack(side="left", expand=True, fill="x", padx=5)
        self.quality_combo.bind("<<ComboboxSelected>>", self.update_filesize)

        self.filesize_label = tk.Label(quality_frame, text="File Size: N/A", font=self.app_font, bg="#f0f0f0")
        self.filesize_label.pack(side="left", padx=10)

        # Add audio-only checkbox
        self.audio_only_var = tk.BooleanVar()
        self.audio_only_check = tk.Checkbutton(quality_frame, 
                                             text="Audio Only",
                                             variable=self.audio_only_var,
                                             command=self.toggle_audio_only,
                                             font=self.app_font,
                                             bg="#f0f0f0")
        self.audio_only_check.pack(side="right", padx=10)


        # Save Location (inside a LabelFrame, below quality)
        location_frame = tk.LabelFrame(options_frame, text="Save Location", font=self.app_font, bg="#f0f0f0", padx=10, pady=5)
        location_frame.pack(fill="x", pady=10) # Added pady for spacing

        self.location_entry = tk.Entry(location_frame, font=self.app_font, width=40)
        self.location_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.location_entry.bind("<Button-3>", self.show_context_menu)
        self.set_default_download_path()
        self.browse_btn = tk.Button(location_frame, text="Browse", command=self.browse_location, font=self.app_font, bg="#4CAF50", fg="white", padx=10)
        self.browse_btn.pack(side="right")



        # Download Button
        self.download_button = tk.Button(root, text="Download", command=self.start_download, font=self.app_font, bg="#4CAF50", fg="white", padx=20, pady=10, state=tk.DISABLED)
        self.download_button.pack()

        # Progress Frame
        self.info_frame = tk.Frame(root, bg="#f0f0f0")
        self.info_frame.pack(fill="x", padx=20, pady=10)
        self.progress_label = tk.Label(self.info_frame, text="", font=self.app_font, bg="#f0f0f0", wraplength=800)
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(self.info_frame, length=500, mode='determinate')
        self.progress_bar.pack(pady=5)

        # Context menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all_text)

        # Store formats
        self.available_formats = []


    def show_context_menu(self, event):
        """Displays the context menu."""
        try:
            pass  # Add your logic here
        except Exception as e:
            print(f"An error occurred: {e}")
            widget = event.widget
            if widget == self.url_entry or widget == self.location_entry:
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def cut_text(self):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Entry):
                widget.event_generate("<<Cut>>")
        except: pass

    def copy_text(self):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Entry):
                widget.event_generate("<<Copy>>")
        except: pass

    def paste_text(self):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Entry):
                widget.event_generate("<<Paste>>")
        except: pass

    def select_all_text(self):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Entry):
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
        except: pass


    def set_default_download_path(self):
        """Sets the default download path."""
        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(downloads_path):
                os.makedirs(downloads_path)
            self.location_entry.insert(0, downloads_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not set default download path: {e}")
            self.location_entry.insert(0, os.getcwd())

    def browse_location(self):
        """Opens a dialog to choose the download location."""
        directory = filedialog.askdirectory(initialdir=self.location_entry.get())
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)

    def load_thumbnail(self, url):
        """Loads and displays the video thumbnail."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            target_width = 320
            ratio = target_width / img.width
            target_height = int(img.height * ratio)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.current_thumbnail = photo
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except:
            messagebox.showwarning("Thumbnail Error", "Could not load thumbnail.")

    def format_size(self, size_bytes):
        """Formats file size in a human-readable way."""
        if not size_bytes:
            return "N/A"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0

    def get_video_info(self):
        """Gets video information (formats, thumbnail) using yt-dlp."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        self.info_btn.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Fetching video information...")
        self.progress_bar['value'] = 0
        self.available_formats = []
        self.quality_combo.set('')
        self.filesize_label.config(text="File Size: N/A")

        def fetch_info():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': "in_playlist",
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    
                    if "entries" in info_dict:
                        info_dict = info_dict['entries'][0]
                    
                    if not info_dict:
                        raise Exception("Could not retrieve video information")

                    thumbnail_url = info_dict.get('thumbnail')
                    if thumbnail_url:
                        self.root.after(0, lambda: self.load_thumbnail(thumbnail_url))

                    formats = info_dict.get('formats', [])
                    if not formats:
                        raise Exception("No formats found")

                    formatted_formats = []
                    # Add best audio+video combined option
                    formatted_formats.append((
                        "Best Quality (Auto)", 
                        "bestvideo*+bestaudio/best", 
                        None
                    ))
                    
                    # Add specific formats
                    for f in formats:
                        format_id = f.get('format_id', '')
                        ext = f.get('ext', 'N/A')
                        filesize = f.get('filesize')
                        filesize_str = self.format_size(filesize) if filesize else "N/A"
                        
                        # Check if it's an audio-only format
                        is_audio_only = f.get('vcodec') == 'none'
                        
                        if is_audio_only:
                            acodec = f.get('acodec', 'N/A')
                            abr = f.get('abr', 'N/A')
                            display_str = f"Audio Only - {acodec} - {abr}kbps - {ext} - {filesize_str}"
                        else:
                            height = f.get('height', 'N/A')
                            vcodec = f.get('vcodec', 'N/A')
                            fps = f.get('fps', 'N/A')
                            acodec = f.get('acodec', 'N/A')
                            resolution = f"{height}p" if height != 'N/A' else 'N/A'
                            
                            # Only add formats with both video and audio, or video-only formats
                            if acodec != 'none' or is_audio_only:
                                display_str = f"{resolution} - {vcodec} - {fps}fps - {acodec} - {ext} - {filesize_str}"
                                formatted_formats.append((display_str, format_id, filesize))

                    self.available_formats = formatted_formats
                    self.root.after(0, lambda: [
                        self.update_format_list(),
                        self.download_button.config(state=tk.NORMAL),
                        self.info_btn.config(state=tk.NORMAL),
                        self.progress_label.config(text=f"Video Title: {info_dict.get('title', 'N/A')}")
                    ])

            except Exception as e:
                self.root.after(0, lambda: [
                    messagebox.showerror("Error", str(e)),
                    self.info_btn.config(state=tk.NORMAL)
                ])

        threading.Thread(target=fetch_info).start()

    def update_filesize(self, event=None):
        """Updates the filesize label."""
        selected_index = self.quality_combo.current()
        if selected_index == -1:
            self.filesize_label.config(text="File Size: N/A")
            return
        try:
            selected_size = self.available_formats[selected_index][2]
            self.filesize_label.config(text=f"File Size: {self.format_size(selected_size)}")
        except IndexError:
            self.filesize_label.config(text="File Size: N/A")

    def start_download(self):
        """Starts the download."""
        if not self.url_entry.get():
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        if not self.location_entry.get():
            messagebox.showerror("Error", "Please select a save location.")
            return

        selected_index = self.quality_combo.current()
        if selected_index == -1:
            messagebox.showerror("Error", "Please select a quality.")
            return

        self.download_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Starting download...")
        self.progress_bar['value'] = 0

        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        """Downloads the video using yt-dlp."""
        url = self.url_entry.get()
        output_path = self.location_entry.get()
        selected_index = self.quality_combo.current()
        
        if selected_index < 0:
            messagebox.showerror("Error", "Please select a quality")
            return
            
        selected_format = self.available_formats[selected_index][1]
        is_audio_only = "Audio Only" in self.available_formats[selected_index][0]

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': selected_format,
            'progress_hooks': [self.yt_dlp_progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        if self.audio_only_var.get() or is_audio_only:
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'format': 'bestaudio/best',
            })
        else:
            # For video downloads, ensure we merge the formats if needed
            ydl_opts.update({
                'format': selected_format,
                'merge_output_format': 'mp4',
            })

        try:
            self.download_button.config(state=tk.DISABLED)
            self.progress_label.config(text="Starting download...")
            self.progress_bar['value'] = 0

            def download_thread():
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    self.root.after(0, lambda: [
                        self.progress_label.config(text="Download complete!"),
                        messagebox.showinfo("Success", "Download completed successfully!"),
                        self.download_button.config(state=tk.NORMAL)
                    ])
                except Exception as e:
                    self.root.after(0, lambda: [
                        messagebox.showerror("Error", str(e)),
                        self.download_button.config(state=tk.NORMAL)
                    ])

            threading.Thread(target=download_thread).start()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.download_button.config(state=tk.NORMAL)

    def yt_dlp_progress_hook(self, d):
        """Callback for yt-dlp progress updates."""
        if d['status'] == 'downloading':
            try:
                # Calculate percentage from downloaded bytes and total size
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0)
                if total:
                    percentage = (downloaded / total) * 100
                else:
                    # Fall back to estimated total bytes if available
                    total = d.get('total_bytes_estimate', 0)
                    if total:
                        percentage = (downloaded / total) * 100
                    else:
                        # If no size info available, use provided percentage
                        percentage = float(d['_percent_str'].replace('%', '').strip())

                # Update progress bar
                self.root.after(0, lambda: [
                    self.progress_bar.config(value=percentage),
                    self.progress_label.config(
                        text=f"Downloading: {d['_percent_str']} • "
                             f"Size: {d.get('_total_bytes_str', 'N/A')} • "
                             f"Speed: {d.get('_speed_str', 'N/A')}"
                    ),
                    self.root.update_idletasks()
                ])
            except Exception as e:
                print(f"Progress error: {e}")
        elif d['status'] == 'finished':
            self.root.after(0, lambda: [
                self.progress_bar.config(value=100),
                self.progress_label.config(text="Download complete! Processing file...")
            ])

    def toggle_audio_only(self):
        """Toggles between audio-only and video formats."""
        self.update_format_list()

    def update_format_list(self):
        """Updates the format list based on audio-only selection."""
        if not self.available_formats:
            return
            
        filtered_formats = []
        for fmt in self.available_formats:
            display_str, format_id, filesize = fmt
            if self.audio_only_var.get():
                if "Audio Only" in display_str:
                    filtered_formats.append(fmt)
            else:
                if "Audio Only" not in display_str:
                    filtered_formats.append(fmt)
        
        self.quality_combo.config(values=[f[0] for f in filtered_formats])
        if filtered_formats:
            self.quality_combo.set(filtered_formats[0][0])
            self.update_filesize()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()