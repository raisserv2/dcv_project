import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
dash.register_page(__name__, path="/builder", name="Arena-wise Stats")
JSON_FILE = "card_percentage_dict.json" #<-- CHECK THIS PATH
try:
    with open(JSON_FILE, 'r') as f:
        card_data = json.load(f)
    all_cards_list = sorted(list(card_data.keys()))
    card_options = [{"label": card, "value": card} for card in all_cards_list]
except Exception as e:
    print(f"CRITICAL ERROR: Could not load {JSON_FILE}. {e}")
    card_data = {}
    card_options = []
layout = dbc.Container(
    [
        html.H2("Card-wise Arena Usage"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Select Card"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Select a card to see its usage % across all arenas:",
                                            className="card-text",
                                        ),
                                        dcc.Dropdown(
                                            id="card-selector",
                                            options=card_options,
                                            placeholder="Select a card...",
                                            clearable=False,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Card(
                            [
                                dbc.CardHeader("Arena-wise Usage Plot"),
                                dbc.CardBody(
                                    [
                                        # The graph will be rendered here
                                        dcc.Graph(id="arena-graph")
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=10,
                    xl=8,  # Center the content on large screens
                )
            ],
            justify="center",
        ),
    ],
    fluid=True,
)
@callback(
    Output("arena-graph", "figure"),
    Input("card-selector", "value"),
)
def update_arena_plot(selected_card):
    # This is the default empty state before a card is selected
    if not selected_card:
        fig = go.Figure()
        fig.update_layout(
            title="Please select a card from the dropdown",
            template="plotly_dark",  # Match your dark theme
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
        )
        return fig
    card_arena_data = card_data.get(selected_card, {})
    all_arenas_x = [str(a) for a in range(1, 25)]
    plot_y_data = [card_arena_data.get(arena_num, 0.0) for arena_num in all_arenas_x]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=all_arenas_x,
            y=plot_y_data,
            name=selected_card,
            mode='lines+markers',
            line=dict(width=3, shape='spline', smoothing=0.8),  # Smooth line
            marker=dict(size=8),
            hovertemplate=(  # Custom hover text
                f'<b>{selected_card}</b><br>'
                'Arena: %{x}<br>'
                'Usage: %{y:.1f}%<extra></extra>'
            ),
        )
    )
    fig.update_layout(
        title=f'Usage Percentage for "{selected_card}" (Arenas 2-25)',
        xaxis_title="Arena Number",
        yaxis_title="Usage Percentage (%)",
        template="plotly_dark",  # Use the dark theme
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(rangemode='tozero', gridcolor='#444'), # Faint gridlines
        xaxis=dict(showgrid=False), # Clean x-axis
        height=500
    )
    return fig