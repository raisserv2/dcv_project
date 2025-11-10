# pages/arena_comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import json
from collections import defaultdict

dash.register_page(__name__, path="/arena", name="Arena Comparison")

# --- 1. Load and Process Usage Rate Data (JSON) ---
JSON_FILE_PATH = "../#2 Data Storage/Visualization Data/card_percentage_dict.json" # Assumes file is in root app folder
print(f"Loading data from {JSON_FILE_PATH}...")
arena_to_usage_map = defaultdict(dict)
all_arenas_int = range(1, 25) # Arenas 1-24
all_arenas_str = [str(i) for i in all_arenas_int]

try:
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        card_data = json.load(f)
    
    # Invert data to {Arena: {Card: %}}
    for card_name, arena_data in card_data.items():
        for arena_num_str in all_arenas_str:
            percent = arena_data.get(arena_num_str, 0.0)
            if percent > 0:
                arena_to_usage_map[arena_num_str][card_name] = percent
    print("Usage rate data loaded.")
except FileNotFoundError:
    print(f"Error: Could not find {JSON_FILE_PATH}")

# --- 2. Load and Process Win Rate Data (CSV) ---
WINLOSS_CSV_PATH = "../#2 Data Storage/Visualization Data/arenawise_card_win_loss.csv" # Assumes file is in root app folder
arena_to_winrate_map = defaultdict(dict)
try:
    df_winloss = pd.read_csv(WINLOSS_CSV_PATH)
    
    # Convert "Arena 1" to "1" to match the slider/JSON data
    df_winloss['arena_num_str'] = df_winloss['arena'].str.split(' ').str[1]
    
    # Sum up counts, ignoring evo (group by arena, card, outcome)
    df_grouped = df_winloss.groupby(['arena_num_str', 'card_name', 'outcome'])['count'].sum().unstack(fill_value=0)
    
    THRESHOLD = 20
    
    # Calculate total matches
    df_grouped['Total_Matches'] = df_grouped['Won'] + df_grouped['Lost']
    
    # Filter the DataFrame to only include rows above the threshold
    df_filtered = df_grouped[df_grouped['Total_Matches'] > THRESHOLD].copy()
    
    # Calculate win rate ONLY on the filtered data
    df_filtered['Win_Rate'] = (df_filtered['Won'] / df_filtered['Total_Matches']).fillna(0) * 100
    
    # Build the nested dictionary map from the FILTERED data
    for (arena_num, card), win_rate in df_filtered['Win_Rate'].items():
        if win_rate > 0:
            arena_to_winrate_map[arena_num][card] = win_rate
            
    print("Win rate data loaded and processed.")
except FileNotFoundError:
    print(f"Error: Could not find {WINLOSS_CSV_PATH}")

# --- 3. Create Dropdown and Slider Options ---
# Cleaner marks - label 1, 24, and every 5th arena
arena_slider_marks = {i: f'{i}' for i in all_arenas_int}
top_n_dropdown_options = [{'label': f'Top {n}', 'value': n} for n in range(3, 11)]


# --- 4. REUSABLE FIGURE FUNCTION (Modified) ---
def create_top_n_figure(selected_arena, selected_top_n, selected_metric):
    """
    Creates the horizontal "Top N" bar chart for the
    selected arena, N value, and metric (usage/winrate).
    """
    if not selected_arena or not selected_top_n:
        return go.Figure(layout={"title": "Please select an Arena and Top N value",
                                 "template": "plotly_dark",
                                 "font": {"family": "'Clash Regular', Arial, sans-serif"}
                                 })

    # Select the correct data source and chart properties based on the metric
    if selected_metric == 'usage':
        data_map = arena_to_usage_map.get(str(selected_arena), {})
        title_text = f"Top {selected_top_n} Most Used Cards in Arena {selected_arena}"
        xaxis_title = "Usage Percentage (%)"
        marker_color = '#17BECF' # Cyan
    else: # 'winrate'
        data_map = arena_to_winrate_map.get(str(selected_arena), {})
        title_text = f"Top {selected_top_n} Highest Win Rate Cards in Arena {selected_arena}"
        xaxis_title = "Win Rate (%)"
        marker_color = '#2ECC71' # Green

    # Sort cards by the selected metric
    sorted_cards = sorted(data_map.items(), key=lambda item: item[1], reverse=True)
    top_n_data = sorted_cards[:selected_top_n]
    
    cards = [item[0] for item in top_n_data]
    percentages = [item[1] for item in top_n_data]

    fig = go.Figure(data=[
        go.Bar(
            orientation='h',
            x=percentages,
            y=cards,
            marker_color=marker_color
        )
    ])
    
    fig.update_layout(
        title_text=title_text,
        template='plotly_dark',
        xaxis_title=xaxis_title,
        yaxis_title="Card Name",
        yaxis=dict(autorange='reversed'),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Clash Regular', Arial, sans-serif",
            size=14,
            color="#FFFFFF"
        ),
        # This overrides just the main title to use the 'Clash Bold' font
        title_font=dict(
            family="'Clash Bold', Arial, sans-serif",
            size=20
        ),
        # This makes the axis titles bold as well
        xaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif"
        ),
        yaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif"
        ) 
    )
    
    return fig

# --- 5. PAGE LAYOUT (Modified Layout) ---
layout = dbc.Container(
    [
        html.H2("Top N Card Usage & Win Rate by Arena"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Controls"),
                    dbc.CardBody([
                        dbc.Row([
                            # Arena Slider
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
                            ], md=6), # Adjusted width
                            # Top N Dropdown
                            dbc.Col([
                                html.Label("Show Top N Cards:"),
                                dcc.Dropdown(
                                    id='top-n-dropdown',
                                    options=top_n_dropdown_options,
                                    value=5 # Default to Top 5
                                )
                            ], md=4), # Adjusted width
                            # --- NEW: Metric Toggle ---
                            dbc.Col([
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
                            ], md=2) # New column
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

# --- 6. CALLBACK (Modified Callback) ---
@dash.callback(
    Output('top-n-graph', 'figure'),
    Input('arena-slider', 'value'),
    Input('top-n-dropdown', 'value'),
    Input('metric-toggle', 'value') # --- NEW INPUT ---
)
def update_graph(selected_arena, selected_top_n, selected_metric):
    # Pass all three inputs to the figure function
    return create_top_n_figure(selected_arena, selected_top_n, selected_metric)