# YouTube Video Downloader

A Python application with a graphical user interface for downloading YouTube videos.

## Features

- User-friendly graphical interface
- Video quality selection
- Download progress tracking
- Video thumbnail preview
- Custom save location
- File size information

## Requirements

- Python 3.x
- Required packages are listed in `requirements.txt`

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python youdwn.py
```

2. Enter a YouTube URL
3. Click "Get Info" to load video information
4. Select desired quality
5. Choose save location (optional)
6. Click "Download" to start downloading

## Dependencies

- tkinter
- pytube
- Pillow
- requests