# pages/arena_comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import ast

dash.register_page(__name__, path="/arena", name="Arena Comparison")

# --- 1. ARENA DICTIONARY (Runs once) ---
arenas_df = pd.read_csv("../#2 Data Storage/Utils/arenas.csv")
arenas_dict = {}

for row in arenas_df.itertuples():
    arenas_dict[row.Arena_ID] = row.Arena_Name

# Load Troop Names
troop_file_name = '../#2 Data Storage/Utils/troop_name.csv' 
troop_df = pd.read_csv(troop_file_name)
troop_list = troop_df['Troop_name'].unique()
troop_set = set(troop_list) 

# Load Battle Log Data
file_name = '../#2 Data Storage/Processed Data/preprocessed_battle_log.csv' 
df = pd.read_csv(file_name)

# Process data for ALL troops
card_data = [] 
for row in df.itertuples(index=False):
    try:
        player_0_cards = {card[0] for card in ast.literal_eval(row.players_0_spells) if isinstance(card, tuple) and len(card) > 0}
    except (ValueError, SyntaxError, TypeError):
        player_0_cards = set()
    try:
        player_1_cards = {card[0] for card in ast.literal_eval(row.players_1_spells) if isinstance(card, tuple) and len(card) > 0}
    except (ValueError, SyntaxError, TypeError):
        player_1_cards = set()

    player_0_troops_used = player_0_cards.intersection(troop_set)
    player_1_troops_used = player_1_cards.intersection(troop_set)

    for troop_name in player_0_troops_used:
        card_data.append({'arena': row.arena, 'outcome': 'Won' if row.players_0_winner == 1 else 'Lost', 'card_name': troop_name})
    for troop_name in player_1_troops_used:
        card_data.append({'arena': row.arena, 'outcome': 'Won' if row.players_1_winner == 1 else 'Lost', 'card_name': troop_name})

# Create and Group the master DataFrame
all_data_df = pd.DataFrame(card_data)
grouped_df = all_data_df.groupby(['arena', 'card_name', 'outcome']).size().reset_index(name='count')
grouped_df['arena'] = grouped_df['arena'].map(arenas_dict)
grouped_df = grouped_df.dropna(subset=['arena'])

# Create master arena order and dropdown options
arena_order = sorted(list(set(grouped_df['arena'])), key=lambda x: int(x.split(' ')[1]))
troops_with_data = sorted(grouped_df['card_name'].unique())
troop_dropdown_options = [{'label': troop, 'value': troop} for troop in troops_with_data]

print("Data processing complete. Dash app is ready.")

# --- 3. REUSABLE FIGURE FUNCTION ---
def create_troop_figure(selected_troop):
    """
    Filters the global grouped_df and returns a Plotly figure
    for the selected troop.
    """
    if not selected_troop:
        return go.Figure(layout={"title": "Please select a troop"})

    fig = go.Figure()
    df_troop = grouped_df[grouped_df['card_name'] == selected_troop]
    
    df_won = df_troop[df_troop['outcome'] == 'Won']
    df_lost = df_troop[df_troop['outcome'] == 'Lost']
    
    # Add Won Trace
    fig.add_trace(go.Bar(
        x=df_won['arena'], y=df_won['count'], name='Won',
        marker_color='blue', 
        hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Won<br>Count: %{{y}}<extra></extra>",
        opacity=0.5 
    ))
    # Add Lost Trace
    fig.add_trace(go.Bar(
        x=df_lost['arena'], y=df_lost['count'], name='Lost',
        marker_color='red', 
        hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Lost<br>Count: %{{y}}<extra></extra>",
        opacity=0.5
    ))
    
    fig.update_layout(
        title_text=f"{selected_troop} Usage: Win vs. Loss",
        xaxis_title="Arena",
        yaxis_title="Usage Count",
        barmode='overlay'
    )
    
    # Apply sorting fix
    fig.update_xaxes(categoryorder='array', categoryarray=arena_order)
    
    return fig

# --- 4. PAGE LAYOUT (Modified from your template) ---
layout = dbc.Container(
    [
        html.H2("Troop 1 vs. Troop 2 Arena Comparison"),
        html.Hr(),
        dbc.Row([
            # --- Column 1: Troop 1 ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Select Troop 1"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='troop-1-dropdown',
                            options=troop_dropdown_options,
                            value=troops_with_data[0] # Default to first troop
                        ),
                        dcc.Graph(
                            id='troop-1-graph'
                        )
                    ])
                ])
            ], md=6),
            
            # --- Column 2: Troop 2 ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Select Troop 2"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='troop-2-dropdown',
                            options=troop_dropdown_options,
                            value=troops_with_data[1] # Default to second troop
                        ),
                        dcc.Graph(
                            id='troop-2-graph'
                        )
                    ])
                ])
            ], md=6),
        ]),
    ],
    fluid=True,
)

# --- 5. CALLBACKS (To make it interactive) ---

# Callback for Troop 1 Graph
@callback(
    Output('troop-1-graph', 'figure'),
    Input('troop-1-dropdown', 'value')
)
def update_graph_1(selected_troop):
    return create_troop_figure(selected_troop)

# Callback for Troop 2 Graph
@callback(
    Output('troop-2-graph', 'figure'),
    Input('troop-2-dropdown', 'value')
)
def update_graph_2(selected_troop):
    return create_troop_figure(selected_troop)
