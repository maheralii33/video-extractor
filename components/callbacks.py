import os
import base64
import json
import logging
from datetime import datetime
from dash import Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
from dash import html
import tempfile
from utils.video_processor import VideoProcessor
from components.pages import (
    create_home_page,
    create_gallery_page,
    create_settings_page,
    create_stats_page,
    create_uploads_page
)

logger = logging.getLogger(__name__)

def register_callbacks(app):
    # Theme switching callback
    @app.callback(
        [
            Output('main-content', 'className'),
            Output('theme-switch', 'children'),
            Output('theme-store', 'data')
        ],
        Input('theme-switch', 'n_clicks'),
        State('theme-store', 'data')
    )
    def switch_theme(n_clicks, theme_data):
        if not n_clicks:
            # Initialize with dark theme if no theme data
            is_dark = theme_data.get('is_dark', True) if theme_data else True
        else:
            # Toggle theme
            is_dark = not (theme_data.get('is_dark', True) if theme_data else True)
        
        return (
            'dark-theme' if is_dark else 'light-theme',
            html.I(className='fas fa-moon' if is_dark else 'fas fa-sun'),
            {'is_dark': is_dark}
        )

    # Navbar toggle callback
    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Page routing and active state callback
    @app.callback(
        [
            Output('page-content', 'children'),
            Output('home-link', 'data-active'),
            Output('uploads-link', 'data-active'),
            Output('gallery-link', 'data-active'),
            Output('settings-link', 'data-active'),
            Output('stats-link', 'data-active')
        ],
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/' or pathname == '':
            return create_home_page(), "true", "false", "false", "false", "false"
        elif pathname == '/gallery':
            return create_gallery_page(), "false", "false", "true", "false", "false"
        elif pathname == '/settings':
            return create_settings_page(), "false", "false", "false", "true", "false"
        elif pathname == '/stats':
            return create_stats_page(), "false", "false", "false", "false", "true"
        elif pathname == '/uploads':
            return create_uploads_page(), "false", "true", "false", "false", "false"
        else:
            return create_home_page(), "true", "false", "false", "false", "false"
    
    # Video processing callback
    @app.callback(
        [Output('processing-status', 'children'),
         Output('processing-progress', 'value'),
         Output('gallery-grid', 'children'),
         Output('process-button', 'disabled')],
        [Input('process-button', 'n_clicks'),
         Input('upload-video', 'contents')],
        [State('frame-rate-slider', 'value'),
         State('confidence-slider', 'value')],
        prevent_initial_call=True
    )
    def process_video_callback(n_clicks, contents, frame_rate, confidence):
        # Handle file upload state
        if contents is None:
            return 'Upload a video to begin', 0, [], True
        
        # If upload-video triggered the callback, just enable the button
        if ctx.triggered_id == 'upload-video':
            return 'Ready to process', 0, [], False
        
        # If neither button was clicked nor file uploaded
        if n_clicks is None:
            return no_update, no_update, no_update, no_update
        
        try:
            logger.info("Starting video processing")
            
            # Decode video content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(decoded)
                temp_path = tmp_file.name
                logger.info(f"Saved uploaded video to temporary file: {temp_path}")
            
            try:
                # Process video
                processor = VideoProcessor()
                extracted_images = processor.process_video(temp_path, frame_rate, confidence)
                
                # Auto-enhance extracted images
                from utils.image_enhancer import ImageEnhancer
                enhancer = ImageEnhancer()
                
                # Apply enhancements to each extracted image
                for img_data in extracted_images:
                    img_path = os.path.join('extracted', img_data['filename'])
                    if os.path.exists(img_path):
                        try:
                            # Apply multiple enhancements automatically
                            methods = ['color', 'denoise', 'sharpen', 'face']
                            enhanced_path = enhancer.enhance_image(img_path, methods)
                            
                            # Update the base64 data with enhanced image
                            with open(enhanced_path, 'rb') as f:
                                img_data['base64'] = base64.b64encode(f.read()).decode('utf-8')
                        except Exception as e:
                            logger.error(f"Error enhancing image {img_path}: {str(e)}")
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info("Cleaned up temporary video file")
            
            # Handle no detections
            if not extracted_images:
                logger.info("No humans detected in video")
                return 'No humans detected in video', 100, [], False
            
            # Create gallery items
            logger.info(f"Creating gallery with {len(extracted_images)} images")
            gallery_items = []
            
            for i, img_data in enumerate(extracted_images):
                gallery_items.append(
                    dbc.Col([
                        dbc.Card([
                            # Image container with hover effect
                            html.Div([
                                dbc.CardImg(
                                    src=f'data:image/jpeg;base64,{img_data["base64"]}',
                                    style={
                                        'height': '350px',
                                        'objectFit': 'cover',
                                    },
                                    className='img-hover'
                                ),
                                # Download button overlay
                                html.A(
                                    dbc.Button(
                                        html.I(className="fas fa-download"),
                                        color="light",
                                        size="sm",
                                        className="download-btn"
                                    ),
                                    href=f'data:image/jpeg;base64,{img_data["base64"]}',
                                    download=f'frame_{img_data["frame"]}.jpg',
                                    className="download-overlay"
                                )
                            ], className="image-container"),
                            
                            # Card body with blog-style content
                            dbc.CardBody([
                                html.Div([
                                    # Title and metadata
                                    html.H5(f"Extracted Frame {img_data['frame']}", className="frame-title"),
                                    html.Div([
                                        html.Span([
                                            html.I(className="far fa-calendar-alt me-2"),
                                            datetime.strptime(img_data['timestamp'], "%Y%m%d_%H%M%S").strftime("%B %d, %Y")
                                        ], className="me-3"),
                                        html.Span([
                                            html.I(className="fas fa-camera me-2"),
                                            "AI Extracted"
                                        ])
                                    ], className="frame-metadata"),
                                    
                                    # Tags
                                    html.Div([
                                        dbc.Badge("Human", color="primary", className="me-2"),
                                        dbc.Badge("Extracted", color="success", className="me-2"),
                                        dbc.Badge(f"Frame {img_data['frame']}", color="info")
                                    ], className="mt-3")
                                ], className="frame-info")
                            ], className="p-3")
                        ], className="frame-card")
                    ], xs=12, sm=6, lg=4, className="mb-4")
                )
            
            # Create gallery grid with gutter
            gallery = dbc.Container([
                dbc.Row(gallery_items, className="gallery-grid")
            ], fluid=True)
            
            logger.info("Gallery creation complete")
            return 'Processing complete!', 100, gallery, False
            
        except Exception as e:
            logger.error(f"Error in video processing: {str(e)}")
            return f'Error: {str(e)}', 0, [], False
    
    # Gallery page callbacks
    @app.callback(
        Output('saved-gallery', 'children'),
        Input('url', 'pathname')
    )
    def update_gallery(pathname):
        if pathname != '/gallery':
            return no_update
        
        try:
            gallery_items = []
            
            # Get all extraction directories
            extracted_dir = 'extracted'
            if not os.path.exists(extracted_dir):
                return html.P("No extracted images found", className="text-muted text-center py-5")
            
            # List all batch directories
            batches = sorted(os.listdir(extracted_dir), reverse=True)
            
            for batch in batches:
                batch_dir = os.path.join(extracted_dir, batch)
                if not os.path.isdir(batch_dir):
                    continue
                
                # Read metadata
                metadata_path = os.path.join(batch_dir, 'metadata.json')
                if not os.path.exists(metadata_path):
                    continue
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Get all images in this batch
                images = [f for f in os.listdir(batch_dir) if f.endswith('.jpg')]
                
                for img_name in sorted(images):
                    img_path = os.path.join(batch_dir, img_name)
                    frame_num = int(img_name.split('_')[1].split('.')[0])
                    
                    # Read image and convert to base64
                    with open(img_path, 'rb') as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    gallery_items.append(
                        dbc.Col([
                            dbc.Card([
                                html.Div([
                                    dbc.CardImg(
                                        src=f'data:image/jpeg;base64,{img_base64}',
                                        style={
                                            'height': '350px',
                                            'objectFit': 'cover',
                                        },
                                        className='img-hover'
                                    ),
                                    html.A(
                                        dbc.Button(
                                            html.I(className="fas fa-download"),
                                            color="light",
                                            size="sm",
                                            className="download-btn"
                                        ),
                                        href=f'data:image/jpeg;base64,{img_base64}',
                                        download=f'frame_{frame_num}.jpg',
                                        className="download-overlay"
                                    )
                                ], className="image-container"),
                                dbc.CardBody([
                                    html.Div([
                                        html.H5(f"Extracted Frame {frame_num}", className="frame-title"),
                                        html.Div([
                                            html.Span([
                                                html.I(className="far fa-calendar-alt me-2"),
                                                datetime.strptime(metadata['timestamp'], "%Y%m%d_%H%M%S").strftime("%B %d, %Y")
                                            ], className="me-3"),
                                            html.Span([
                                                html.I(className="fas fa-camera me-2"),
                                                "AI Extracted"
                                            ])
                                        ], className="frame-metadata"),
                                        html.Div([
                                            dbc.Badge("Human", color="primary", className="me-2"),
                                            dbc.Badge("Extracted", color="success", className="me-2"),
                                            dbc.Badge(f"Frame {frame_num}", color="info")
                                        ], className="mt-3")
                                    ], className="frame-info")
                                ], className="p-3")
                            ], className="frame-card")
                        ], xs=12, sm=6, lg=4, className="mb-4")
                    )
            
            if not gallery_items:
                return html.P("No extracted images found", className="text-muted text-center py-5")
            
            return dbc.Row(gallery_items, className="gallery-grid")
            
        except Exception as e:
            logger.error(f"Error loading gallery: {str(e)}")
            return html.P(f"Error loading gallery: {str(e)}", className="text-danger text-center py-5")
    

