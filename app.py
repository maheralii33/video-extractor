import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import base64
from datetime import datetime
from flask import Flask
from utils.video_processor import VideoProcessor
from components.layout import create_layout
from components.callbacks import register_callbacks
from components.admin import create_admin_layout
from components.admin_callbacks import register_admin_callbacks

# Initialize Flask server
server = Flask(__name__)
server.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize the main Dash app
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
        '/assets/custom.css'
    ],
    suppress_callback_exceptions=True,
    url_base_pathname='/'
)

# Initialize the admin Dash app
admin_app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
        '/assets/custom.css'
    ],
    suppress_callback_exceptions=True,
    url_base_pathname='/admin/'
)

# Set the titles
app.title = "For you Sudan"
admin_app.title = "Admin Dashboard - For you Sudan"

# Create the layouts
app.layout = create_layout()
admin_app.layout = create_admin_layout()

# Register callbacks
register_callbacks(app)
register_admin_callbacks(admin_app)

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('extracted', exist_ok=True)
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=8050)
