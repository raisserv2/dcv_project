import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import pandas as pd
from collections import defaultdict
import pickle
import numpy as np
import networkx as nx

dash.register_page(__name__, path="/evo", name="Evo Analysis")

# --- 1. NEW: Win Rate Subplot Function ---
def create_win_rate_subplot(evo_df, non_evo_df, min_plays=100):
    """Creates a 1x2 subplot for Top Win Rate cards"""
    categories = [
        (
            "Top EVO Cards (by Win %)",
            evo_df[evo_df["total_plays"] >= min_plays].nlargest(10, "win_percentage"),
            "win_percentage"
        ),
        (
            "Top NON-EVO Cards (by Win %)",
            non_evo_df[non_evo_df["total_plays"] >= min_plays].nlargest(10, "win_percentage"),
            "win_percentage"
        ),
    ]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[cat[0] for cat in categories],
        horizontal_spacing=0.1
    )

    for i, (title, data, x_axis_key) in enumerate(categories):
        col = i + 1
        color = "#C118D4" if "EVO" in title else "#2E7DE4"
        x_title = "Win Rate (%)"
        text_template = "%{x:.1f}%"

        fig.add_trace(
            go.Bar(
                x=data[x_axis_key],
                y=data["card"],
                orientation="h",
                marker_color=color,
                name=title,
                text=data[x_axis_key],
                texttemplate=text_template,
                textposition='auto',
                hovertemplate=f"<b>Card:</b> %{{y}}<br><b>{x_title}:</b> %{{x}}<extra></extra>"
            ),
            row=1, col=col,
        )
        fig.update_yaxes(autorange="reversed", row=1, col=col)
        fig.update_xaxes(title_text=x_title, row=1, col=col)

    fig.update_layout(
        height=500,
        title_text="Top Performers by Win Rate",
        template="plotly_dark",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Clash Regular', Arial, sans-serif", size=12, color="#FFFFFF"),
        title_font=dict(family="'Clash Bold', Arial, sans-serif", size=20),
        annotations=[dict(font=dict(family="'Clash Bold', Arial, sans-serif", size=16, color="#FFFFFF"))]
    )
    fig.update_xaxes(title_font=dict(family="'Clash Bold', Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="'Clash Bold', Arial, sans-serif"))
    return fig

# --- 2. NEW: Usage Count Subplot Function ---
def create_usage_subplot(evo_df, non_evo_df):
    """Creates a 1x2 subplot for Most Used cards"""
    categories = [
        ("Most Used EVO", evo_df.nlargest(10, "usage_count"), "usage_count"),
        ("Most Used NON-EVO", non_evo_df.nlargest(10, "usage_count"), "usage_count"),
    ]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[cat[0] for cat in categories],
        horizontal_spacing=0.1
    )

    for i, (title, data, x_axis_key) in enumerate(categories):
        col = i + 1
        color = "#C118D4" if "EVO" in title else "#2E7DE4"
        x_title = "Usage Count"
        text_template = "%{x:,}"

        fig.add_trace(
            go.Bar(
                x=data[x_axis_key],
                y=data["card"],
                orientation="h",
                marker_color=color,
                name=title,
                text=data[x_axis_key],
                texttemplate=text_template,
                textposition='auto',
                hovertemplate=f"<b>Card:</b> %{{y}}<br><b>{x_title}:</b> %{{x}}<extra></extra>"
            ),
            row=1, col=col,
        )
        fig.update_yaxes(autorange="reversed", row=1, col=col)
        fig.update_xaxes(title_text=x_title, row=1, col=col)

    fig.update_layout(
        height=500,
        title_text="Most Used Cards",
        template="plotly_dark",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Clash Regular', Arial, sans-serif", size=12, color="#FFFFFF"),
        title_font=dict(family="'Clash Bold', Arial, sans-serif", size=20),
        annotations=[dict(font=dict(family="'Clash Bold', Arial, sans-serif", size=16, color="#FFFFFF"))]
    )
    fig.update_xaxes(title_font=dict(family="'Clash Bold', Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="'Clash Bold', Arial, sans-serif"))
    return fig

# --- (Other figure functions: create_evo_impact_analysis, etc. are unchanged) ---
def create_evo_impact_analysis(evo_df, non_evo_df):
    """Analyze the impact of evolution on card performance"""
    all_cards = set(evo_df["card"]).union(set(non_evo_df["card"]))
    comparison_data = []

    for card in all_cards:
        evo_data = evo_df[evo_df["card"] == card]
        non_evo_data = non_evo_df[non_evo_df["card"] == card]

        if len(evo_data) > 0 and len(non_evo_data) > 0:
            evo_win = evo_data.iloc[0]["win_percentage"]
            non_evo_win = non_evo_data.iloc[0]["win_percentage"]
            win_rate_change = evo_win - non_evo_win

            comparison_data.append(
                {
                    "card": card,
                    "evo_win_rate": evo_win,
                    "non_evo_win_rate": non_evo_win,
                    "win_rate_change": win_rate_change,
                    "has_improvement": win_rate_change > 0,
                }
            )

    comparison_df = pd.DataFrame(comparison_data).sort_values(by="win_rate_change", ascending=False)

    fig = px.bar(
        comparison_df,
        x="card",
        y="win_rate_change",
        color="has_improvement",
        title="EVO Impact: Win Rate Change vs NON-EVO Version",
        labels={"win_rate_change": "Win Rate Change (%)", "card": "Card"},
        color_discrete_map={True: "#2E7DE4", False: "#C118D4"},
    )

    fig.update_layout(
        xaxis_tickangle=-60, # Changed from -45 for longer names
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", # <-- ADDED
        plot_bgcolor="rgba(0,0,0,0)",  # <-- ADDED
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
            family="'Clash Bold', Arial, sans-serif",
        ),
        yaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif",
        )
    )
    return fig

def create_evo_comparison_bubble(combined_df, min_plays=50):
    """Compare EVO vs NON-EVO performance"""
    df_filtered = combined_df[combined_df["total_plays"] >= min_plays]

    fig = px.scatter(
        df_filtered,
        x="usage_count",
        y="win_percentage",
        color="card_type",
        size="total_plays",
        hover_name="card",
        title="EVO vs NON-EVO Card Performance",
        labels={"usage_count": "Usage Count", "win_percentage": "Win Rate (%)"},
        color_discrete_map={"EVO": "#C118D4", "NON_EVO": "#2E7DE4"},
    )

    # --- MODIFICATIONS START ---
    fig.update_layout(
        height=600,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
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
            family="'Clash Bold', Arial, sans-serif",
        ),
        yaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif",
        )
    )
    # --- MODIFICATIONS END ---
    return fig

def create_comprehensive_evo_dashboard(evo_df, non_evo_df):
    """
    Shows EVO vs NON-EVO performance grouped by elixir cost.
    """
    
    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=evo_df["win_percentage"],
            x=evo_df["elixir_cost"],
            name="EVO",
            marker_color="#C118D4",
        )
    )
    
    fig.add_trace(
        go.Box(
            y=non_evo_df["win_percentage"],
            x=non_evo_df["elixir_cost"],
            name="NON-EVO",
            marker_color="#2E7DE4",
        )
    )
    
    fig.update_layout(
        height=500, 
        title_text="Performance by Elixir Cost (EVO vs NON-EVO)",
        xaxis_title="Elixir Cost",
        yaxis_title="Win Rate (%)",
        boxmode='group',
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", # <-- ADDED
        plot_bgcolor="rgba(0,0,0,0)",  # <-- ADDED
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
            family="'Clash Bold', Arial, sans-serif",
        ),
        yaxis_title_font=dict(
            family="'Clash Bold', Arial, sans-serif",
        )
    )

    return fig


# --- 3. DATA LOADING (Unchanged) ---
card_db_path = "../#2 Data Storage/Visualization Data/card_database.csv"
battle_data_path = "../#2 Data Storage/Visualization Data/clash_royale_data_separated.pkl"

try:
    card_db = pd.read_csv(card_db_path)
    print(f"✓ Loaded card database: {len( card_db)} cards")
except Exception as e:
    print(f"Error loading card_db: {e}")
    card_db = pd.DataFrame(columns=['englishName', 'elixir_cost', 'rarity', 'is_evo'])

try:
    with open(battle_data_path, 'rb') as f:
        battle_data = pickle.load(f)
except Exception as e:
    print(f"Error loading battle_data: {e}")
    battle_data = {
        'evo': {'usage': {}, 'wins': {}, 'total_plays': {}, 'win_percentage': {}},
        'non_evo': {'usage': {}, 'wins': {}, 'total_plays': {}, 'win_percentage': {}}
    }

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
if not card_db.empty:
    evo_df =  evo_df.merge(
        card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
        left_on='card', right_on='englishName', how='left'
    ).drop('englishName', axis=1)
    non_evo_df =  non_evo_df.merge(
        card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
        left_on='card', right_on='englishName', how='left'
    ).drop('englishName', axis=1)
combined_df = pd.concat([ evo_df,  non_evo_df], ignore_index=True)


# --- 4. Create Static Figures (Runs once on startup) ---
# --- MODIFICATION: Removed top_performers from here ---
fig_impact_analysis = create_evo_impact_analysis(evo_df, non_evo_df)
fig_comparison_bubble = create_evo_comparison_bubble(combined_df)
fig_comprehensive = create_comprehensive_evo_dashboard(evo_df, non_evo_df)


# --- 5. NEW LAYOUT (Modified) ---
layout = dbc.Container(
    [
        html.Div(
            html.H1("Clash Royale Evolution Analysis", className="text-center"),
            className="page-title-container"
        ),
        
        # --- MODIFICATION: Added Toggle and put Graph in Card ---
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Top Performing Cards"), # Simplified header
                        dbc.CardBody([
                            # --- NEW RADIO TOGGLE ---
                            dcc.RadioItems(
                                id='top-performers-toggle',
                                options=[
                                    {'label': 'Top by Win Rate', 'value': 'win_rate'},
                                    {'label': 'Most Used', 'value': 'usage_count'}
                                ],
                                value='win_rate', # Default selection
                                className="dbc",
                                inline=True,
                                style={'marginBottom': '15px', 'width': '100%', 'textAlign': 'center'}
                            ),
                            # --- END NEW TOGGLE ---
                            
                            # Graph is now empty, will be filled by callback
                            dcc.Graph(id="top-performers") 
                        ])
                    ]), 
                    width=12
                ),
            ],
            className="mb-4"
        ),
        
        # --- (Other chart cards are unchanged) ---
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("EVO Impact: Win Rate Change vs NON-EVO"),
                        dbc.CardBody([
                            dcc.Graph(id="impact-analysis", figure=fig_impact_analysis)
                        ])
                    ]), 
                    width=12
                ),
            ],
            className="mb-4"
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("EVO vs NON-EVO Card Performance"),
                        dbc.CardBody([
                            dcc.Graph(id="comparison-bubble", figure=fig_comparison_bubble)
                        ])
                    ]), 
                    width=12
                ),
            ],
            className="mb-4"
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Performance by Elixir Cost (EVO vs NON-EVO)"),
                        dbc.CardBody([
                            dcc.Graph(id="comprehensive-dashboard", figure=fig_comprehensive)
                        ])
                    ]), 
                    width=12
                ),
            ],
            className="mb-4"
        ),
    ],
    fluid=True,
)

# --- 6. NEW CALLBACK ---
@dash.callback(
    Output("top-performers", "figure"),
    Input("top-performers-toggle", "value")
)
def update_top_performers_graph(selected_metric):
    min_plays = 100 # Keep the min_plays consistent
    if selected_metric == 'win_rate':
        return create_win_rate_subplot(evo_df, non_evo_df, min_plays)
    else: # 'usage_count'
        return create_usage_subplot(evo_df, non_evo_df)