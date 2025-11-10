# pages/arena_comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import json
from collections import defaultdict

dash.register_page(__name__, path="/arena", name="Arena Comparison")

# --- 1. Load and Process Data (from your ipywidgets code) ---
JSON_FILE_PATH = "../#2 Data Storage/Visualized Data/card_percentage_dict.json" # Assumed path
print(f"Loading data from {JSON_FILE_PATH}...")

try:
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        card_data = json.load(f)
    
    # Invert data to {Arena: {Card: %}}
    arena_to_card_map = defaultdict(dict)
    all_arenas_int = range(1, 25) # Arenas 1-24
    all_arenas_str = [str(i) for i in all_arenas_int]

    for card_name, arena_data in card_data.items():
        for arena_num_str in all_arenas_str:
            percent = arena_data.get(arena_num_str, 0.0)
            if percent > 0:
                arena_to_card_map[arena_num_str][card_name] = percent
    
    print("Data processing complete. Dash app is ready.")

    # --- Create Dropdown and Slider Options ---
    arena_slider_marks = {i: f'{i}' for i in all_arenas_int}
    
    top_n_dropdown_options = [
        {'label': f'Top {n}', 'value': n} for n in range(3, 20)
    ]

except FileNotFoundError:
    print(f"Error: Could not find {JSON_FILE_PATH}")
    print("Please make sure the JSON file exists at that path.")
    # Set empty options if file fails to load
    arena_to_card_map = defaultdict(dict)
    arena_slider_marks = {}
    top_n_dropdown_options = []


# --- 3. REUSABLE FIGURE FUNCTION (New function) ---
def create_top_n_figure(selected_arena, selected_top_n):
    """
    Creates the horizontal "Top N" bar chart for the
    selected arena and N value.
    """
    if not selected_arena or not selected_top_n:
        return go.Figure(layout={
            "title": "Please select an Arena and Top N value", 
            "template": "plotly_dark"
        })

    # Get the card data for the selected arena
    card_usage_map = arena_to_card_map.get(str(selected_arena), {})
    
    # Sort cards by percentage and get the top N
    sorted_cards = sorted(card_usage_map.items(), key=lambda item: item[1], reverse=True)
    top_n_data = sorted_cards[:selected_top_n]
    
    # Unzip the data into two lists
    # No reverse needed for this orientation
    cards = [item[0] for item in top_n_data]
    percentages = [item[1] for item in top_n_data]

    fig = go.Figure(data=[
        go.Bar(
            orientation='h', # Horizontal bar chart
            x=percentages,
            y=cards,
            marker_color='#17BECF' # Plotly Cyan
        )
    ])
    
    fig.update_layout(
        title_text=f"Top {selected_top_n} Most Used Cards in Arena {selected_arena}",
        template='plotly_dark',
        xaxis_title="Usage Percentage (%)",
        yaxis_title="Card Name",
        yaxis=dict(autorange='reversed'), # Puts highest value at the top
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

# --- 4. PAGE LAYOUT (New Layout) ---
layout = dbc.Container(
    [
        html.H2("Top N Card Usage by Arena"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Controls"),
                    dbc.CardBody([
                        dbc.Row([
                            # Arena Dropdown
                            dbc.Col([
                                html.Label("Select Arena:"),
                                dcc.Slider(
                                    id='arena-slider',
                                    min=min(all_arenas_int),
                                    max=max(all_arenas_int),
                                    step=1,
                                    value=min(all_arenas_int),
                                    marks=arena_slider_marks
                                )
                            ], md=6),
                            # Top N Dropdown
                            dbc.Col([
                                html.Label("Show Top N Cards:"),
                                dcc.Dropdown(
                                    id='top-n-dropdown',
                                    options=top_n_dropdown_options,
                                    value=10 # Default to Top 10
                                )
                            ], md=6),
                        ]),
                        html.Hr(),
                        # The Graph
                        dcc.Graph(id='top-n-graph')
                    ])
                ])
            ], width=12),
        ]),
    ],
    fluid=True,
)

# --- 5. CALLBACK (New Callback) ---
@dash.callback(
    Output('top-n-graph', 'figure'),
    Input('arena-slider', 'value'),
    Input('top-n-dropdown', 'value')
)
def update_graph(selected_arena, selected_top_n):
    return create_top_n_figure(selected_arena, selected_top_n)