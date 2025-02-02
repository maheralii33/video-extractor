from dash import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
import psutil
import plotly.graph_objs as go
from datetime import datetime, timedelta

def register_admin_callbacks(app):
    @app.callback(
        [Output("cpu-usage", "children"),
         Output("memory-usage", "children"),
         Output("disk-usage", "children"),
         Output("cpu-progress", "value"),
         Output("memory-progress", "value"),
         Output("disk-progress", "value"),
         Output("metrics-history", "data"),
         Output("system-metrics-graph", "figure")],
        [Input("metrics-update-interval", "n_intervals"),
         State("metrics-history", "data")]
    )
    def update_metrics(n_intervals, history):
        # Get current metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Update history
        current_time = datetime.now().strftime("%H:%M:%S")
        history['cpu'].append(cpu_percent)
        history['memory'].append(memory.percent)
        history['disk'].append(disk.percent)
        history['time'].append(current_time)
        
        # Keep only last 30 points
        if len(history['time']) > 30:
            history['cpu'] = history['cpu'][-30:]
            history['memory'] = history['memory'][-30:]
            history['disk'] = history['disk'][-30:]
            history['time'] = history['time'][-30:]
        
        # Create graph
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=history['time'],
            y=history['cpu'],
            name="CPU",
            line=dict(color="#0d6efd")
        ))
        
        fig.add_trace(go.Scatter(
            x=history['time'],
            y=history['memory'],
            name="Memory",
            line=dict(color="#ffc107")
        ))
        
        fig.add_trace(go.Scatter(
            x=history['time'],
            y=history['disk'],
            name="Disk",
            line=dict(color="#198754")
        ))
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(
                showgrid=True,
                gridcolor='#eee',
                range=[0, 100],
                title="Percentage (%)"
            )
        )
        
        # Return all updated values
        return (
            f"{cpu_percent:.1f}%",
            f"{memory.percent:.1f}%",
            f"{disk.percent:.1f}%",
            cpu_percent,
            memory.percent,
            disk.percent,
            history,
            fig
        )

    @app.callback(
        [Output("total-videos", "children"),
         Output("total-images", "children"),
         Output("avg-time", "children")],
        [Input("metrics-update-interval", "n_intervals")]
    )
    def update_processing_stats(n_intervals):
        # Here you would normally get these values from your database
        # For now, we'll use placeholder values
        total_videos = len(os.listdir('uploads')) if os.path.exists('uploads') else 0
        total_images = len(os.listdir('extracted')) if os.path.exists('extracted') else 0
        avg_time = "2.5s"  # Placeholder
        
        return str(total_videos), str(total_images), avg_time
