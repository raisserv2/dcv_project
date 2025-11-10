# pages/custom_builder.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
# Note: Removed 'defaultdict' and 'pandas' as they are no longer needed

# --- Register Page (Updated Name) ---
dash.register_page(__name__, path="/builder", name="Card & Arena Analysis")

# --- 1. Load and Prepare Data ---
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

# --- 2. Define the Layout (Only Section 1) ---
layout = dbc.Container(
    [
        # --- SECTION 1: Card-wise Arena Usage ---
        html.H2("Card-wise Arena Usage"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Select Card(s)"),
                                dbc.CardBody(
                                    [
                                        html.P("Select one or more cards to compare:", className="card-text"),
                                        dcc.Dropdown(
                                            id="card-selector",
                                            options=card_options,
                                            placeholder="Select card(s)...",
                                            multi=True, 
                                            clearable=True,
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
                                    [dcc.Graph(id="arena-graph")]
                                ),
                            ]
                        ),
                    ],
                    width=12, lg=10, xl=8, # Centered column
                )
            ],
            justify="center",
        ),
        
        # --- SECTION 2 (Removed) ---
    ],
    fluid=True,
)

# --- 3. CALLBACK ---
# Callback for the (Top) Line Plot
@callback(
    Output("arena-graph", "figure"),
    Input("card-selector", "value"), # This is now a list
)
def update_arena_plot(selected_cards):
    
    # Create the base figure
    fig = go.Figure()

    # Default empty state
    if not selected_cards:
        fig.update_layout(
            title="Please select one or more cards from the dropdown",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
        )
        return fig

    # --- One or more cards ARE selected ---
    
    # Define the common X-axis
    all_arenas_x = [str(a) for a in range(2, 26)]

    # Loop through each selected card and add a line (trace) for it
    for card_name in selected_cards:
        card_arena_data = card_data.get(card_name, {})
        plot_y_data = [card_arena_data.get(arena_num, 0.0) for arena_num in all_arenas_x]

        fig.add_trace(
            go.Scatter(
                x=all_arenas_x,
                y=plot_y_data,
                name=card_name, # Adds the card to the legend
                mode='lines+markers',
                line=dict(width=3, shape='spline', smoothing=0.8),
                marker=dict(size=8),
                hovertemplate=(
                    f'<b>{card_name}</b><br>'
                    'Arena: %{x}<br>'
                    'Usage: %{y:.1f}%<extra></extra>'
                ),
            )
        )

    # Style the figure for your dark theme
    fig.update_layout(
        title='Usage Percentage Across Arenas',
        xaxis_title="Arena Number",
        yaxis_title="Usage Percentage (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(rangemode='tozero', gridcolor='#444'),
        xaxis=dict(showgrid=False),
        height=500,
        legend_title_text='Selected Cards'
    )
    return fig