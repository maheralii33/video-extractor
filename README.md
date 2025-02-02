# Video Human Extractor

A powerful web application built with Dash that automatically extracts human pictures from videos using AI-based analysis. The application provides an intuitive interface for uploading videos, processing them to detect and extract human figures, and managing the extracted content.

## Features

- Upload and process videos
- AI-powered human detection using MediaPipe
- Adjustable frame sampling rate and confidence threshold
- Real-time processing progress updates
- Interactive gallery of extracted images
- Bulk download capability for extracted images

## Prerequisites

- Python 3.8+
- Redis server (for Celery task queue)
- OpenCV system dependencies

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd video-extractor
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Start the Redis server:
```bash
redis-server
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8050
```

3. Use the interface to:
   - Upload videos
   - Adjust processing parameters
   - View extracted images
   - Download results

## Project Structure

```
video-extractor/
├── app.py                 # Main application file
├── components/           # Dash components and callbacks
│   ├── callbacks.py
│   └── layout.py
├── utils/               # Utility functions
│   └── video_processor.py
├── uploads/            # Temporary video storage
├── extracted/          # Extracted images storage
└── requirements.txt    # Project dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
