import dash_bootstrap_components as dbc
from dash import html, dcc
import psutil
import plotly.graph_objs as go
from datetime import datetime, timedelta

def create_system_stats():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    stats = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("CPU Usage"),
                dbc.CardBody([
                    html.H2(f"{cpu_percent}%"),
                    dcc.Graph(
                        id='cpu-gauge',
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'mode': 'gauge+number',
                                'value': cpu_percent,
                                'gauge': {'axis': {'range': [0, 100]}},
                            }],
                            'layout': {'height': 150, 'margin': {'t': 0, 'b': 0}}
                        }
                    )
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Memory Usage"),
                dbc.CardBody([
                    html.H2(f"{memory.percent}%"),
                    dcc.Graph(
                        id='memory-gauge',
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'mode': 'gauge+number',
                                'value': memory.percent,
                                'gauge': {'axis': {'range': [0, 100]}},
                            }],
                            'layout': {'height': 150, 'margin': {'t': 0, 'b': 0}}
                        }
                    )
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Disk Usage"),
                dbc.CardBody([
                    html.H2(f"{disk.percent}%"),
                    dcc.Graph(
                        id='disk-gauge',
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'mode': 'gauge+number',
                                'value': disk.percent,
                                'gauge': {'axis': {'range': [0, 100]}},
                            }],
                            'layout': {'height': 150, 'margin': {'t': 0, 'b': 0}}
                        }
                    )
                ])
            ])
        ], width=4),
    ])
    return stats

def create_processing_stats():
    return dbc.Card([
        dbc.CardHeader("Processing Statistics"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Total Videos Processed"),
                    html.H2(id="total-videos", children="0")
                ], width=4),
                dbc.Col([
                    html.H4("Total Images Extracted"),
                    html.H2(id="total-images", children="0")
                ], width=4),
                dbc.Col([
                    html.H4("Average Processing Time"),
                    html.H2(id="avg-time", children="0s")
                ], width=4),
            ])
        ])
    ])

def create_user_management():
    return dbc.Card([
        dbc.CardHeader("User Management"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="user-search", placeholder="Search users..."),
                ], width=8),
                dbc.Col([
                    dbc.Button("Add User", color="primary", id="add-user-btn"),
                ], width=4),
            ]),
            html.Div(id="user-table", className="mt-3"),
        ])
    ])

def create_model_settings():
    return dbc.Card([
        dbc.CardHeader("AI Model Settings"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Detection Model"),
                    dcc.Dropdown(
                        id="detection-model",
                        options=[
                            {"label": "MediaPipe", "value": "mediapipe"},
                            {"label": "YOLO", "value": "yolo"},
                            {"label": "OpenPose", "value": "openpose"}
                        ],
                        value="mediapipe"
                    )
                ], width=6),
                dbc.Col([
                    html.Label("Default Confidence Threshold"),
                    dcc.Slider(
                        id="default-confidence",
                        min=0.1,
                        max=1.0,
                        step=0.1,
                        value=0.5,
                        marks={i/10: str(i/10) for i in range(1, 11)}
                    )
                ], width=6),
            ]),
            dbc.Button("Save Settings", color="success", className="mt-3", id="save-settings-btn")
        ])
    ])

def create_admin_layout():
    return dbc.Container([
        html.H1("Admin Dashboard", className="text-center my-4"),
        html.Hr(),
        
        # System Statistics
        html.H3("System Status", className="mb-3"),
        create_system_stats(),
        html.Hr(),
        
        # Processing Statistics
        html.H3("Processing Statistics", className="mb-3"),
        create_processing_stats(),
        html.Hr(),
        
        # User Management
        html.H3("User Management", className="mb-3"),
        create_user_management(),
        html.Hr(),
        
        # Model Settings
        html.H3("AI Model Settings", className="mb-3"),
        create_model_settings(),
        
        # Update interval for real-time stats
        dcc.Interval(id='stats-update', interval=5000),
    ], fluid=True)
