import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
import pickle
import json
from collections import defaultdict
import ast
from typing import Dict, List, Optional
import pickle
import json
from collections import defaultdict
import ast
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import pandas as pd
from collections import defaultdict

dash.register_page(__name__, path="/rarity", name="Rarity Analysis")

# Custom color map for rarities
RARITY_COLORS = {
    "Common": "blue",
    "Rare": "orange",
    "Epic": "purple",
    "Legendary": "green",
    "Champion": "red"
}
DEFAULT_ARCHETYPE_MAPPING = {
    'Beatdown': ['Golem', 'Lava Hound', 'Giant', 'Electro Giant', 'Royal Giant'],
    'Control': ['X-Bow', 'Mortar', 'Tesla', 'Bomb Tower', 'Inferno Tower'],
    'Cycle': ['Hog Rider', 'Miner', 'Wall Breakers', 'Skeletons', 'Ice Spirit'],
    'Spell Bait': ['Goblin Barrel', 'Princess', 'Dart Goblin', 'Goblin Gang'],
    'Bridge Spam': ['Bandit', 'Royal Ghost', 'Battle Ram', 'Dark Prince'],
    'Siege': ['X-Bow', 'Mortar', 'Bomb Tower'],
    'Spawner': ['Goblin Hut', 'Furnace', 'Barbarian Hut', 'Tombstone']
}
# 13. Rarity Performance Violin Plot
def create_rarity_violin_plot(df: pd.DataFrame) -> go.Figure:
    """Violin plot showing win rate distribution by rarity"""
    fig = px.violin(df, x='rarity', y='win_percentage',
                    color='rarity', box=True, points="all",
                    title='Win Rate Distribution by Rarity',
                    color_discrete_map=RARITY_COLORS)
    
    return fig


# 15. Rarity Meta Share Donut Chart
def create_rarity_meta_share(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing rarity distribution in the meta"""
    rarity_share = df.groupby('rarity')['usage_count'].sum().reset_index()
    
    fig = px.pie(rarity_share, values='usage_count', names='rarity',
                 title='Rarity Distribution in Current Meta (by Usage Count)',
                 hole=0.4, color='rarity',
                 color_discrete_map=RARITY_COLORS)
    
    return fig

# 1. Interactive Card Win Rate vs Usage Bubble Chart
def create_win_rate_usage_bubble(df: pd.DataFrame, min_plays: int = 100) -> go.Figure:
    """Win Rate vs Usage with Elixir Cost as bubble size and custom rarity colors"""
    df_filtered = df[df['total_plays'] >= min_plays]
    
    fig = px.scatter(
        df_filtered,
        x='usage_count',
        y='win_percentage',
        size='elixir_cost',
        hover_name='card',
        color='rarity',
        size_max=30,
        title='Card Performance: Win Rate vs Usage (Bubble Size = Elixir Cost)',
        labels={'usage_count': 'Usage Count', 'win_percentage': 'Win Rate (%)'},
        color_discrete_map=RARITY_COLORS
    )
    
    # Add average lines
    avg_usage = df_filtered['usage_count'].mean()
    avg_win = df_filtered['win_percentage'].mean()
    
    fig.add_hline(y=avg_win, line_dash="dash", line_color="red")
    fig.add_vline(x=avg_usage, line_dash="dash", line_color="red")
    
    fig.update_layout(height=600, xaxis_type="log")
    return fig


def prepare_archetype_data(df: pd.DataFrame, mapping: Dict = DEFAULT_ARCHETYPE_MAPPING) -> pd.DataFrame:
    """
    Assigns archetypes to cards in the DataFrame based on a mapping.
    
    Args:
        df: The input DataFrame (must contain a 'card' column).
        mapping: A dictionary defining which cards belong to which archetype.
        
    Returns:
        A new DataFrame with an 'archetype' column added.
    """
    df_out = df.copy()
    df_out['archetype'] = 'Utility'  # Default value
    for archetype, cards in mapping.items():
        mask = df_out['card'].isin(cards)
        df_out.loc[mask, 'archetype'] = archetype
    return df_out

# --- Visualization Functions ---


def load_example_data(card_db_path='card_database.csv', battle_data_path='clash_royale_data_separated.pkl') -> Optional[pd.DataFrame]:
    """
    Loads and merges the example data for visualization.
    This demonstrates the data structure the functions expect.
    """

    
    try:
        # Load card database
        card_db = pd.read_csv(card_db_path)

        
        # Load battle data
        with open(battle_data_path, 'rb') as f:
            battle_data = pickle.load(f)
        
        # Create DataFrames for EVO and NON-EVO
        evo_df = pd.DataFrame({
            'card': list(battle_data['evo']['usage'].keys()),
            'usage_count': list(battle_data['evo']['usage'].values()),
            'win_count': [battle_data['evo']['wins'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
            'total_plays': [battle_data['evo']['total_plays'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
            'win_percentage': [battle_data['evo']['win_percentage'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
            'card_type': 'EVO'
        })
        
        non_evo_df = pd.DataFrame({
            'card': list(battle_data['non_evo']['usage'].keys()),
            'usage_count': list(battle_data['non_evo']['usage'].values()),
            'win_count': [battle_data['non_evo']['wins'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
            'total_plays': [battle_data['non_evo']['total_plays'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
            'win_percentage': [battle_data['non_evo']['win_percentage'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
            'card_type': 'NON_EVO'
        })
        
        # Merge with card database
        evo_df = evo_df.merge(
            card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
            left_on='card', right_on='englishName', how='left'
        ).drop('englishName', axis=1)
        
        non_evo_df = non_evo_df.merge(
            card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
            left_on='card', right_on='englishName', how='left'
        ).drop('englishName', axis=1)
        
        # Create combined DataFrame
        combined_df = pd.concat([evo_df, non_evo_df], ignore_index=True)

        
        # Prepare archetype data
        combined_df = prepare_archetype_data(combined_df, DEFAULT_ARCHETYPE_MAPPING)
        return combined_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Please make sure 'card_database.csv' and 'clash_royale_data_separated.pkl' are present in the same directory.")
        return 


        # 1. Load and prepare data
# This step is now separate from the visualization functions.

card_db_path = "../#2 Data Storage/Visualization Data/card_database.csv"
battle_data_path = "../#2 Data Storage/Visualization Data/clash_royale_data_separated.pkl"

df = load_example_data(card_db_path, battle_data_path)
if df is not None:
    # 2. Create visualizations
    Rarity_Violin = create_rarity_violin_plot(df)
    Rarity_Meta_Share = create_rarity_meta_share(df)
    Win_Rate_Usage_Bubble = create_win_rate_usage_bubble(df, min_plays=100)

    layout = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("Rarity Analysis Dashboard"),
                                html.P("Explore how card rarity impacts performance and usage in the current meta."),
                                dcc.Markdown("""
                                    This dashboard provides insights into the performance of cards based on their rarity.
                                    Analyze win rate distributions, meta share, and the relationship between usage and win rates.
                                """),
                            ],
                            width=12,
                            className="mb-4"
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(figure=Rarity_Violin),
                            width=6
                        ),
                        dbc.Col(
                            dcc.Graph(figure=Rarity_Meta_Share),
                            width=6
                        )
                    ],
                    className="mb-4"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(figure=Win_Rate_Usage_Bubble),
                            width=12
                        )
                    ]
                )
            ],
            fluid=True
        )

else:
    layout = dbc.Container(
        [
            html.H2("Rarity Analysis Dashboard"),
            html.P("Data could not be loaded. Please ensure the required data files are present."),
        ],
        fluid=True
    )