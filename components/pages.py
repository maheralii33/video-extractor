import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import numpy as np
import os
import json

def create_home_page():
    return dbc.Container([
        # Upload Area
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-3x mb-3 text-primary"),
                            html.H4("Upload Video", className="mb-3"),
                            html.P("Click or drag a video file here", className="text-muted"),
                            dcc.Upload(
                                id="upload-video",
                                children=[],
                                multiple=False,
                                className="upload-area"
                            )
                        ], className="text-center")
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Control Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Processing Settings", className="mb-3"),
                        
                        # Frame Rate Slider
                        html.Div([
                            html.Label("Frame Rate (frames to skip)", className="slider-label"),
                            dcc.Slider(
                                id="frame-rate-slider",
                                min=1,
                                max=30,
                                step=1,
                                value=10,
                                marks={1: '1', 10: '10', 20: '20', 30: '30'},
                                className="mb-4"
                            )
                        ], className="slider-container"),
                        
                        # Confidence Threshold Slider
                        html.Div([
                            html.Label("Confidence Threshold", className="slider-label"),
                            dcc.Slider(
                                id="confidence-slider",
                                min=0.1,
                                max=1.0,
                                step=0.1,
                                value=0.5,
                                marks={0.1: '0.1', 0.5: '0.5', 1.0: '1.0'},
                                className="mb-4"
                            )
                        ], className="slider-container"),
                        
                        # Process Button and Status
                        html.Div([
                            dbc.Button(
                                "Process Video",
                                id="process-button",
                                color="primary",
                                className="w-100 mb-3",
                                disabled=True
                            ),
                            dbc.Progress(id="processing-progress", value=0, className="mb-2"),
                            html.P(id="processing-status", className="text-center text-muted")
                        ])
                    ])
                ], className="control-panel")
            ])
        ]),
        
        # Gallery Grid
        html.Div(id="gallery-grid", className="mt-4")
    ], fluid=True)

def create_gallery_page():
    def get_extracted_frames():
        extracted_dir = 'extracted'
        if not os.path.exists(extracted_dir):
            return []
        
        frames = []
        for video_dir in os.listdir(extracted_dir):
            video_path = os.path.join(extracted_dir, video_dir)
            if os.path.isdir(video_path):
                # Get metadata
                meta_path = os.path.join(video_path, 'metadata.json')
                metadata = {}
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        try:
                            metadata = json.load(f)
                        except:
                            pass
                
                # Get frames
                for frame in os.listdir(video_path):
                    if frame.endswith('.jpg') and frame != 'metadata.json':
                        frame_path = os.path.join(video_path, frame)
                        frames.append({
                            'path': frame_path,
                            'name': frame,
                            'video_dir': video_dir,
                            'timestamp': metadata.get('timestamp', video_dir),
                            'frame_number': int(frame.split('_')[1].split('.')[0])
                        })
        
        return sorted(frames, key=lambda x: (x['timestamp'], x['frame_number']), reverse=True)

    frames = get_extracted_frames()
    
    if not frames:
        return dbc.Container([
            html.H1("Image Gallery", className="text-center mb-4"),
            html.Div(
                dbc.Alert("No extracted frames found", color="info"),
                className="text-center"
            )
        ], fluid=True)
    
    # Create frame cards
    frame_cards = []
    for i in range(0, len(frames), 4):  # 4 cards per row
        row_frames = frames[i:i+4]
        row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardImg(
                        src=f"/assets/frames/extracted/{frame['video_dir']}/{frame['name']}",
                        top=True,
                        style={"height": "200px", "objectFit": "cover"}
                    ),
                    dbc.CardBody([
                        html.H5(
                            f"Frame {frame['frame_number']}",
                            className="card-title text-truncate"
                        ),
                        html.P(
                            f"From video: {frame['timestamp']}",
                            className="card-text small text-muted"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-download me-1"),
                            color="primary",
                            size="sm",
                            id={'type': 'download-frame', 'index': frame['path']}
                        )
                    ])
                ], className="h-100 frame-card")
            ], width=3) for frame in row_frames
        ], className="mb-4")
        frame_cards.append(row)
    
    return dbc.Container([
        html.H1("Image Gallery", className="text-center mb-4"),
        
        # Enhancement status
        dbc.Row([
            dbc.Col([
                html.Div(id='enhance-status', className='text-center mb-2'),
                dbc.Progress(id='enhance-progress', value=0, className='mb-4')
            ])
        ]),
        
        # Search and filter controls
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    type="search",
                    placeholder="Search frames...",
                    id="frame-search",
                    className="mb-3"
                )
            ], width=8),
            dbc.Col([
                dbc.Select(
                    id="frame-sort",
                    options=[
                        {"label": "Newest First", "value": "newest"},
                        {"label": "Oldest First", "value": "oldest"},
                        {"label": "Frame Number (Asc)", "value": "frame_asc"},
                        {"label": "Frame Number (Desc)", "value": "frame_desc"}
                    ],
                    value="newest",
                    className="mb-3"
                )
            ], width=4)
        ], className="mb-4"),
        
        # Frame grid
        html.Div(frame_cards)
    ], fluid=True)

def create_settings_page():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Settings", className="mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        # Video Processing Settings
                        html.H5("Video Processing", className="mb-3"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Default Frame Rate"),
                                    dbc.Input(
                                        id="default-frame-rate",
                                        type="number",
                                        min=1,
                                        max=30,
                                        step=1,
                                        value=10
                                    )
                                ], className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Default Confidence Threshold"),
                                    dbc.Input(
                                        id="default-confidence",
                                        type="number",
                                        min=0.1,
                                        max=1.0,
                                        step=0.1,
                                        value=0.5
                                    )
                                ], className="mb-3"),
                            ]),
                            
                            # Storage Settings
                            html.H5("Storage", className="mb-3 mt-4"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Save Extracted Images"),
                                    dbc.Switch(
                                        id="save-images",
                                        value=True
                                    )
                                ], className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Image Format"),
                                    dbc.Select(
                                        id="image-format",
                                        options=[
                                            {"label": "JPEG", "value": "jpg"},
                                            {"label": "PNG", "value": "png"}
                                        ],
                                        value="jpg"
                                    )
                                ], className="mb-3"),
                            ]),
                            
                            # Save Button
                            dbc.Button(
                                "Save Settings",
                                id="save-settings",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True)

def create_uploads_page():
    def get_uploaded_videos():
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            return []
        
        videos = []
        for filename in os.listdir(upload_dir):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                file_path = os.path.join(upload_dir, filename)
                
                # Get processing status and thumbnail from metadata
                meta_path = os.path.join('metadata', f'{filename}.json')
                status = 'Pending'
                thumbnail = None
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        try:
                            meta = json.load(f)
                            status = meta.get('status', 'Pending')
                            # Get first extracted frame as thumbnail if available
                            extracted_dir = os.path.join('extracted', os.path.splitext(filename)[0])
                            if os.path.exists(extracted_dir):
                                frames = [f for f in os.listdir(extracted_dir) if f.endswith('.jpg')]
                                if frames:
                                    thumbnail = os.path.join(extracted_dir, sorted(frames)[0])
                        except:
                            pass
                
                videos.append({
                    'name': filename,
                    'path': file_path,
                    'thumbnail': thumbnail,
                    'status': status
                })
        
        return sorted(videos, key=lambda x: os.path.getmtime(x['path']), reverse=True)

    videos = get_uploaded_videos()
    
    if not videos:
        return dbc.Container([
            html.H1("Video Database", className="text-center mb-4"),
            html.Div(
                dbc.Alert("No videos found in database", color="info"),
                className="text-center"
            )
        ], fluid=True)
    
    # Create video cards
    video_cards = []
    for i in range(0, len(videos), 3):  # 3 cards per row
        row_videos = videos[i:i+3]
        row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardImg(
                        src=video['thumbnail'] if video['thumbnail'] else '/assets/video-placeholder.png',
                        top=True,
                        style={"height": "200px", "objectFit": "cover"}
                    ),
                    dbc.CardBody([
                        html.H5(video['name'], className="card-title text-truncate"),
                        dbc.Badge(
                            video['status'],
                            color={
                                'Pending': 'warning',
                                'Processing': 'info',
                                'Completed': 'success',
                                'Failed': 'danger'
                            }.get(video['status'], 'secondary'),
                            className="mb-2"
                        ),
                        html.Div([
                            dbc.Button(
                                html.I(className="fas fa-play me-1"),
                                color="primary",
                                size="sm",
                                className="me-2",
                                id={'type': 'play-video', 'index': video['name']}
                            ),
                            dbc.Button(
                                html.I(className="fas fa-images me-1"),
                                color="success",
                                size="sm",
                                className="me-2",
                                id={'type': 'view-frames', 'index': video['name']}
                            ),
                            dbc.Button(
                                html.I(className="fas fa-trash"),
                                color="danger",
                                size="sm",
                                id={'type': 'delete-video', 'index': video['name']}
                            )
                        ], className="d-flex justify-content-center")
                    ])
                ], className="h-100 video-card")
            ], width=4) for video in row_videos
        ], className="mb-4")
        video_cards.append(row)
    
    return dbc.Container([
        html.H1("Video Database", className="text-center mb-4"),
        
        # Search and filter controls
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    type="search",
                    placeholder="Search videos...",
                    id="video-search",
                    className="mb-3"
                )
            ], width=8),
            dbc.Col([
                dbc.Select(
                    id="video-filter",
                    options=[
                        {"label": "All Videos", "value": "all"},
                        {"label": "Completed", "value": "completed"},
                        {"label": "Processing", "value": "processing"},
                        {"label": "Pending", "value": "pending"},
                        {"label": "Failed", "value": "failed"}
                    ],
                    value="all",
                    className="mb-3"
                )
            ], width=4)
        ], className="mb-4"),
        
        # Video grid
        html.Div(video_cards)
    ], fluid=True)

def create_stats_page():
    # Generate sample data for the graph
    dates = [datetime.now() - timedelta(days=x) for x in range(7)]
    videos = np.random.randint(1, 10, size=7)
    images = videos * np.random.randint(5, 15, size=7)
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Statistics", className="mb-4"),
                # Stats Cards
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3(
                                    "156",
                                    id="total-videos-processed",
                                    className="text-center text-primary mb-2"
                                ),
                                html.P(
                                    "Videos Processed",
                                    className="text-center text-muted"
                                )
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3(
                                    "1,234",
                                    id="total-images-extracted",
                                    className="text-center text-success mb-2"
                                ),
                                html.P(
                                    "Images Extracted",
                                    className="text-center text-muted"
                                )
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3(
                                    "2.5s",
                                    id="avg-processing-time",
                                    className="text-center text-info mb-2"
                                ),
                                html.P(
                                    "Average Processing Time",
                                    className="text-center text-muted"
                                )
                            ])
                        ])
                    ], width=4)
                ], className="mb-4"),
                
                # Processing History Graph
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Processing History", className="mb-3"),
                        dcc.Graph(
                            id="processing-history-graph",
                            figure={
                                'data': [
                                    go.Scatter(
                                        x=[d.strftime("%Y-%m-%d") for d in dates],
                                        y=videos,
                                        name='Videos',
                                        line=dict(color='#0d6efd')
                                    ),
                                    go.Scatter(
                                        x=[d.strftime("%Y-%m-%d") for d in dates],
                                        y=images,
                                        name='Images',
                                        line=dict(color='#198754')
                                    )
                                ],
                                'layout': go.Layout(
                                    title='Last 7 Days',
                                    xaxis={'title': 'Date'},
                                    yaxis={'title': 'Count'},
                                    template='plotly_white',
                                    height=400,
                                    margin=dict(l=40, r=40, t=40, b=40)
                                )
                            }
                        )
                    ])
                ], className="mb-4"),
                
                # System Resources
                dbc.Card([
                    dbc.CardBody([
                        html.H5("System Resources", className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.P("CPU Usage", className="mb-2"),
                                dbc.Progress(
                                    value=45,
                                    id="cpu-usage",
                                    label="45%",
                                    className="mb-3"
                                )
                            ], width=6),
                            dbc.Col([
                                html.P("Memory Usage", className="mb-2"),
                                dbc.Progress(
                                    value=60,
                                    id="memory-usage",
                                    label="60%",
                                    className="mb-3"
                                )
                            ], width=6)
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True)
