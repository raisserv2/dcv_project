# pages/builder.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import pandas as pd
from collections import defaultdict

# --- Register Page (Updated Name) ---
dash.register_page(__name__, path="/builder", name="Card & Arena Analysis")

# --- 1. Load and Prepare Usage Rate Data (JSON) ---

# <-- FIX: Initialize variables *before* the try block -->
# This ensures they exist even if the file load fails.
usage_rate_data = {}
all_cards_list = []
card_options = []

JSON_FILE = "card_percentage_dict.json" # <-- FIX: Simplified path
try:
    with open(JSON_FILE, 'r') as f:
        # <-- FIX: Load into 'usage_rate_data' to match the callback -->
        usage_rate_data = json.load(f) 
    all_cards_list = sorted(list(usage_rate_data.keys()))
    # <-- FIX: Define card_options here after all_cards_list is created -->
    card_options = [{"label": card, "value": card} for card in all_cards_list]
    print("Usage rate data loaded.")
    
except Exception as e:
    print(f"CRITICAL ERROR: Could not load {JSON_FILE}. {e}")
    # Variables are already initialized as empty, so the app won't crash

    
# --- 2. Load and Prepare Win Rate Data (CSV) ---
# <-- FIX: Simplified path -->
WINLOSS_CSV_PATH = "arenawise_card_win_loss.csv"
win_rate_data = defaultdict(dict) # Structure: {'CardName': {'1': 50.5, '2': 51.2, ...}}
try:
    df_winloss = pd.read_csv(WINLOSS_CSV_PATH)
    
    # Convert "Arena 1" to "1"
    df_winloss['arena_num_str'] = df_winloss['arena'].str.split(' ').str[1]
    
    # Sum up counts (group by arena, card, outcome)
    df_grouped = df_winloss.groupby(['arena_num_str', 'card_name', 'outcome'])['count'].sum().unstack(fill_value=0)
    
    # Calculate win rate
    df_grouped['Total_Matches'] = df_grouped['Won'] + df_grouped['Lost']
    df_grouped['Win_Rate'] = (df_grouped['Won'] / df_grouped['Total_Matches']).fillna(0) * 100
    
    # Build the nested dictionary map {Card: {Arena: WinRate}}
    for (arena_num, card), win_rate in df_grouped['Win_Rate'].items():
        if win_rate > 0:
            win_rate_data[card][arena_num] = win_rate
            
    print("Win rate data loaded and processed.")
except FileNotFoundError:
    print(f"Error: Could not find {WINLOSS_CSV_PATH}")
except Exception as e:
    print(f"An error occurred while processing win rate data: {e}")


# --- 3. Define the Layout (Only Section 1) ---
layout = dbc.Container(
    [
        # --- SECTION 1: Card-wise Arena Usage ---
        html.H2("Card-wise Arena Analysis"), # Renamed title
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Controls"), # Renamed header
                                dbc.CardBody(
                                    [
                                        html.P("Select one or more cards:", className="card-text"),
                                        dcc.Dropdown(
                                            id="card-selector",
                                            # <-- FIX: Use the 'card_options' variable -->
                                            options=card_options,
                                            placeholder="Select card(s)...",
                                            multi=True, 
                                            clearable=True,
                                        ),
                                        html.Br(),
                                        # --- NEW METRIC TOGGLE ---
                                        html.Label("Select Metric:"),
                                        dcc.RadioItems(
                                            id='metric-toggle',
                                            options=[
                                                {'label': 'Usage Rate', 'value': 'usage'},
                                                {'label': 'Win Rate', 'value': 'winrate'}
                                            ],
                                            value='usage', # Default
                                            className="dbc" # Use for better dark theme styling
                                        )
                                        # --- END NEW TOGGLE ---
                                    ]
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Card(
                            [
                                dbc.CardHeader("Arena-wise Metric Plot"), # Renamed header
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

# --- 4. CALLBACK (Modified) ---
@callback(
    Output("arena-graph", "figure"),
    Input("card-selector", "value"), # This is now a list
    Input("metric-toggle", "value"), # --- NEW INPUT ---
)
def update_arena_plot(selected_cards, selected_metric):
    
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
    
    # Define the common X-axis (Arenas 1-24)
    all_arenas_x = [str(a) for a in range(1, 25)]
    
    # --- Select Data Source based on toggle ---
    if selected_metric == 'usage':
        # <-- This now correctly uses 'usage_rate_data' -->
        data_source = usage_rate_data 
        y_axis_title = "Usage Percentage (%)"
        hover_label = "Usage"
        title_text = "Usage Percentage Across Arenas"
    else: # 'winrate'
        data_source = win_rate_data
        y_axis_title = "Win Rate (%)"
        hover_label = "Win Rate"
        title_text = "Win Rate Across Arenas"

    # Loop through each selected card and add a line (trace) for it
    for card_name in selected_cards:
        card_arena_data = data_source.get(card_name, {})
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
                    f'Arena: %{{x}}<br>'
                    f'{hover_label}: %{{y:.1f}}%<extra></extra>' # Dynamic hover
                ),
            )
        )

    # Style the figure for your dark theme
    fig.update_layout(
        title=title_text, # Dynamic title
        xaxis_title="Arena Number",
        yaxis_title=y_axis_title, # Dynamic y-axis title
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        height=500,
        legend_title_text='Selected Cards',
        # --- Add custom fonts ---
        font=dict(
            family="'Clash Regular', Arial, sans-serif",
            size=14,
            color="#FFFFFF"
        ),
        title_font=dict(
            family="'Clash Bold', Arial, sans-serif",
            size=20
        ),
        xaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif"
        ),
        yaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif"
        )
    )
    
    # --- Add 50% line for win rate, or set range for usage ---
    if selected_metric == 'winrate':
        fig.add_hline(
            y=50.0,
            line_dash="dash",
            line_color="white",
        )
        fig.update_yaxes(gridcolor='#444')
    else:
        fig.update_yaxes(rangemode='tozero', gridcolor='#444')
        
    return fig