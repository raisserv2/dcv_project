# pages/player_comparison.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/player", name="Player Comparison")

layout = dbc.Container(
    [
        html.H2("Troop A vs Troop B"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop A Stats"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure={"data": [], "layout": {"title": "Troop A Performance"}}
                        ),
                        dbc.Button("Load Troop A Data", color="info", className="mt-2")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop B Stats"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure={"data": [], "layout": {"title": "Troop B Performance"}}
                        ),
                        dbc.Button("Load Troop B Data", color="info", className="mt-2")
                    ])
                ])
            ], md=6),
        ]),
    ],
    fluid=True,
)
