import dash_bootstrap_components as dbc
from dash import dcc, html
from components.pages import (
    create_home_page,
    create_gallery_page,
    create_settings_page,
    create_stats_page
)

def create_navbar():
    return html.Nav(
        [
            # Left side - Brand with Logo
            html.Div(
                [
                    html.A(
                        [
                            html.Img(src="/assets/logo.svg", height="40px", className="brand-logo me-2"),
                            html.Span("For You Sudan", className="brand-text")
                        ],
                        href="/",
                        className="brand-link d-flex align-items-center"
                    )
                ],
                className="navbar-brand-container"
            ),
            
            # Center - Navigation
            html.Div(
                [
                    dbc.Nav(
                        [
                            html.A(
                                [
                                    html.I(className="fas fa-home"),
                                    html.Span("Home", className="nav-text")
                                ],
                                href="/",
                                className="menu-link",
                                id="home-link"
                            ),
                            html.A(
                                [
                                    html.I(className="fas fa-video"),
                                    html.Span("Uploads", className="nav-text")
                                ],
                                href="/uploads",
                                className="menu-link",
                                id="uploads-link"
                            ),
                            html.A(
                                [
                                    html.I(className="fas fa-images"),
                                    html.Span("Gallery", className="nav-text")
                                ],
                                href="/gallery",
                                className="menu-link",
                                id="gallery-link"
                            ),
                            html.A(
                                [
                                    html.I(className="fas fa-cog"),
                                    html.Span("Settings", className="nav-text")
                                ],
                                href="/settings",
                                className="menu-link",
                                id="settings-link"
                            ),
                            html.A(
                                [
                                    html.I(className="fas fa-chart-bar"),
                                    html.Span("Stats", className="nav-text")
                                ],
                                href="/stats",
                                className="menu-link",
                                id="stats-link"
                            ),
                        ],
                        className="nav-menu"
                    )
                ],
                className="navbar-center"
            ),
            
            # Right side - Theme Toggle
            html.Div(
                [
                    dbc.Button(
                        html.I(className="fas fa-moon"),
                        color="light",
                        className="theme-button",
                        id="theme-switch"
                    )
                ],
                className="navbar-end"
            )
        ],
        id="navbar",
        className="navbar-light py-2 px-4"
    )

def create_footer():
    return html.Footer(
        dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.P([
                        "© 2025 Video Human Extractor. Built with ",
                        html.I(className="fas fa-heart text-danger"),
                        " using Dash and OpenCV."
                    ], className="text-center text-muted")
                ])
            ])
        ], fluid=True),
        className="mt-5 py-3"
    )

def create_layout():
    return html.Div([
        # URL Location
        dcc.Location(id='url', refresh=False),
        
        # Main content wrapper
        html.Div([
            # Navbar
            create_navbar(),
            
            # Content
            html.Div(id='page-content', className='container-fluid'),
            
            # Footer
            create_footer()
        ], id='main-content')
    ])
