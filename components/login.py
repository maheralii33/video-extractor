import dash_bootstrap_components as dbc
from dash import html, dcc

def create_login_form():
    return dbc.Container([
        html.H1("Login", className="text-center my-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Form([
                            dbc.FormGroup([
                                dbc.Label("Username"),
                                dbc.Input(
                                    type="text",
                                    id="username-input",
                                    placeholder="Enter username"
                                ),
                            ]),
                            dbc.FormGroup([
                                dbc.Label("Password"),
                                dbc.Input(
                                    type="password",
                                    id="password-input",
                                    placeholder="Enter password"
                                ),
                            ]),
                            dbc.Button(
                                "Login",
                                color="primary",
                                className="mt-3",
                                id="login-button",
                                n_clicks=0
                            ),
                            html.Div(id="login-error", className="text-danger mt-3"),
                        ])
                    ])
                ])
            ], width=6, className="mx-auto")
        ])
    ])
