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
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import pandas as pd
from collections import defaultdict


dash.register_page(__name__, path="/deck", name="Deck Archetypes")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pickle
import json
from collections import defaultdict
import ast
from typing import Dict, List, Optional

# --- Data Preparation & Constants ---

# Default archetype mapping, can be overridden by passing a custom dict
DEFAULT_ARCHETYPE_MAPPING = {
    'Beatdown': ['Golem', 'Lava Hound', 'Giant', 'Electro Giant', 'Royal Giant'],
    'Control': ['X-Bow', 'Mortar', 'Tesla', 'Bomb Tower', 'Inferno Tower'],
    'Cycle': ['Hog Rider', 'Miner', 'Wall Breakers', 'Skeletons', 'Ice Spirit'],
    'Spell Bait': ['Goblin Barrel', 'Princess', 'Dart Goblin', 'Goblin Gang'],
    'Bridge Spam': ['Bandit', 'Royal Ghost', 'Battle Ram', 'Dark Prince'],
    'Siege': ['X-Bow', 'Mortar', 'Bomb Tower'],
    'Spawner': ['Goblin Hut', 'Furnace', 'Barbarian Hut', 'Tombstone']
}


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


#
# 7. Deck Archetype Sunburst Chart
def create_archetype_sunburst(df: pd.DataFrame) -> go.Figure:
    """
    Sunburst chart of archetypes and cards.
    Requires 'archetype' column (run prepare_archetype_data first).
    """
    if 'archetype' not in df.columns:
        print("Warning: 'archetype' column not found. Run prepare_archetype_data() first.")
        return go.Figure()

    sunburst_data = []
    
    for archetype in df['archetype'].unique():
        archetype_cards = df[df['archetype'] == archetype]
        total_usage = archetype_cards['usage_count'].sum()
        avg_win_rate = archetype_cards['win_percentage'].mean()
        
        # Archetype level
        sunburst_data.append({
            'ids': archetype,
            'labels': archetype,
            'parents': '',
            'values': total_usage,
            'win_rate': avg_win_rate
        })
        
        # Card level
        for _, card in archetype_cards.iterrows():
            sunburst_data.append({
                'ids': f"{archetype}-{card['card']}",
                'labels': card['card'],
                'parents': archetype,
                'values': card['usage_count'],
                'win_rate': card['win_percentage']
            })
    
    df_sunburst = pd.DataFrame(sunburst_data)
    
    fig = px.sunburst(df_sunburst, path=['parents', 'labels'], values='values',
                      color='win_rate', color_continuous_scale='RdYlGn',
                      title='Deck Archetype Hierarchy and Performance')
    
    return fig

# 12. Card Performance Treemap
def create_card_treemap(df: pd.DataFrame, min_plays: int = 30) -> go.Figure:
    """
    Treemap showing card performance.
    Requires 'archetype' column (run prepare_archetype_data first).
    """
    if 'archetype' not in df.columns:
        print("Warning: 'archetype' column not found. Run prepare_archetype_data() first.")
        return go.Figure()
        
    df_filtered = df[df['total_plays'] >= min_plays]
    
    fig = px.treemap(df_filtered, path=['rarity', 'archetype', 'card'],
                     values='usage_count', color='win_percentage',
                     color_continuous_scale='RdYlGn',
                     title='Card Performance Treemap (Size=Usage, Color=Win Rate)')
    
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig



# --- Example Usage ---

def load_example_data(card_db_path='card_database.csv', battle_data_path='clash_royale_data_separated.pkl') -> Optional[pd.DataFrame]:
    """
    Loads and merges the example data for visualization.
    This demonstrates the data structure the functions expect.
    """
    print("🚀 Loading example data...")
    
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
    Archetype_Sunburst = create_archetype_sunburst(df)
    Card_Treemap = create_card_treemap(df)


layout = dbc.Container(
    [
        html.Div(
            html.H2("Deck Archetypes Visualization"),
            className="page-title-container"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure=Archetype_Sunburst),
                    width=12
                )
            ],
            className="mb-4"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure=Card_Treemap),
                    width=12
                )
            ]
        )
    ],
    fluid=True
)   