# pages/custom_builder.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/custom_builder", name="Custom Builder")

troop_options = [f"Troop {i}" for i in range(1, 21)]

layout = dbc.Container(
    [
        html.H2("Custom Builder – Select 8 Troops"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop Selection"),
                    dbc.CardBody([
                        html.P("Choose up to 8 troops:"),
                        dcc.Dropdown(
                            options=[{"label": t, "value": t} for t in troop_options],
                            multi=True,
                            placeholder="Select troops...",
                            maxHeight=300,
                            id="troop-selector",
                        ),
                        dbc.Button("Confirm Selection", color="success", className="mt-3"),
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Preview"),
                    dbc.CardBody([
                        html.Div(id="troop-preview", children="Your selected troops will appear here."),
                        dcc.Graph(
                            figure={"data": [], "layout": {"title": "Troop Strength Chart"}}
                        )
                    ])
                ])
            ], md=6),
        ]),
    ],
    fluid=True,
)
