# YouTube Video Downloader

A Python application with a graphical user interface for downloading YouTube videos.

## Features

- User-friendly graphical interface
- Video quality selection with file size information
- Video thumbnail preview
- Custom save location
- Download progress tracking
- Support for multiple video qualities

## Requirements

- Python 3.x
- Required packages listed in `requirements.txt`

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

2. Enter a YouTube URL in the input field
3. Click "Get Info" to load video information and available qualities
4. Select your desired video quality from the dropdown menu
5. (Optional) Choose a custom save location
6. Click "Download" to start downloading the video

## Dependencies

- tkinter (GUI framework)
- pytube (YouTube video downloading)
- Pillow (Image processing)
- requests (HTTP requests)