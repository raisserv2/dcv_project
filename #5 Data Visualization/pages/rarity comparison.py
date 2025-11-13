# pages/rarity comparison.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
from collections import defaultdict
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/rarity", name="Rarity Analysis")

# --- MODIFIED: Updated with your requested colors in dark-mode shades ---
RARITY_COLORS = {
    "Common": "#5DADE2",    # Light Blue
    "Rare": "#F39C12",      # Orange
    "Epic": "#AF7AC5",      # Purple
    "Legendary": "#2ECC71", # Green
    "Champion": "#E74C3C"   # Red
}

# --- UNUSED: Removed DEFAULT_ARCHETYPE_MAPPING ---

# 13. Rarity Performance Violin Plot
def create_rarity_violin_plot(df: pd.DataFrame) -> go.Figure:
    """Violin plot showing win rate distribution by rarity"""
    fig = px.violin(df, x='rarity', y='win_percentage',
                    color='rarity', box=True,
                    title='Win Rate Distribution by Rarity',
                    color_discrete_map=RARITY_COLORS)
    
    # --- MODIFICATION: Apply Theme ---
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Clash Regular', Arial, sans-serif", size=14, color="#FFFFFF"),
        title_font=dict(family="'Clash Bold', Arial, sans-serif", size=20),
        xaxis_title_font=dict(family="'Clash Bold', Arial, sans-serif"),
        yaxis_title_font=dict(family="'Clash Bold', Arial, sans-serif")
    )
    return fig


# 15. Rarity Meta Share Donut Chart
def create_rarity_meta_share(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing rarity distribution in the meta"""
    rarity_share = df.groupby('rarity')['usage_count'].sum().reset_index()
    
    fig = px.pie(rarity_share, values='usage_count', names='rarity',
                 title='Rarity Distribution in Current Meta',
                 hole=0.4, color='rarity',
                 color_discrete_map=RARITY_COLORS)
    
    # --- MODIFICATION: Apply Theme ---
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Clash Regular', Arial, sans-serif", size=14, color="#FFFFFF"),
        title_font=dict(family="'Clash Bold', Arial, sans-serif", size=20)
    )
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
    
    fig.add_hline(y=avg_win, line_dash="dash", line_color="#E74C3C") # Red
    fig.add_vline(x=avg_usage, line_dash="dash", line_color="#E74C3C") # Red
    
    # --- MODIFICATION: Apply Theme ---
    fig.update_layout(
        height=600, 
        xaxis_type="log",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Clash Regular', Arial, sans-serif", size=14, color="#FFFFFF"),
        title_font=dict(family="'Clash Bold', Arial, sans-serif", size=20),
        xaxis_title_font=dict(family="'Clash Bold', Arial, sans-serif"),
        yaxis_title_font=dict(family="'Clash Bold', Arial, sans-serif")
    )
    return fig

# --- UNUSED: Removed prepare_archetype_data function ---

def load_example_data(card_db_path='card_database.csv', battle_data_path='clash_royale_data_separated.pkl') -> pd.DataFrame:
    """
    Loads and merges the example data for visualization.
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
        
        # --- MODIFICATION: Corrected path assumption ---
        print("✓ Rarity data loaded successfully.")
        return combined_df
        
    except Exception as e:
        print(f"❌ Error loading data for Rarity page: {e}")
        return None

# --- 1. Load and prepare data ---
# --- MODIFICATION: Corrected paths to be relative to app.py ---
card_db_path = "../#2 Data Storage/Visualization Data/card_database.csv"
battle_data_path = "../#2 Data Storage/Visualization Data/clash_royale_data_separated.pkl"

df = load_example_data(card_db_path, battle_data_path)

# --- 2. Create Layout ---
if df is not None:
    # 2. Create visualizations
    Rarity_Violin = create_rarity_violin_plot(df)
    Rarity_Meta_Share = create_rarity_meta_share(df)
    Win_Rate_Usage_Bubble = create_win_rate_usage_bubble(df, min_plays=100)

    layout = dbc.Container(
        [
            # --- MODIFICATION: Added page-title-container ---
            html.Div(
                [
                    html.H2("Rarity Analysis")
                ],
                className="page-title-container"
            ),
            
            # --- MODIFICATION: Wrapped graphs in Cards ---
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("Win Rate Distribution by Rarity"),
                            dbc.CardBody([
                                dcc.Graph(id="rarity-violin", figure=Rarity_Violin)
                            ])
                        ]),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("Rarity Distribution in Current Meta"),
                            dbc.CardBody([
                                dcc.Graph(id="rarity-meta", figure=Rarity_Meta_Share)
                            ])
                        ]),
                        width=6
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("Card Performance: Win Rate vs Usage"),
                            dbc.CardBody([
                                dcc.Graph(id="rarity-comparison-bubble", figure=Win_Rate_Usage_Bubble)
                            ])
                        ]),
                        width=12
                    )
                ]
            )
        ],
        fluid=True
    )

else:
    # Error layout
    layout = dbc.Container(
        [
            html.Div(
                html.H2("Rarity Analysis Dashboard"),
                className="page-title-container"
            ),
            dbc.Alert(
                "Data could not be loaded. Please ensure 'card_database.csv' and 'clash_royale_data_separated.pkl' are present in the correct folder.",
                color="danger",
                className="mt-4"
            )
        ],
        fluid=True
    )