# pages/arena_comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import ast

dash.register_page(__name__, path="/arena", name="Arena Comparison")

grouped_df = pd.read_csv("../#2 Data Storage/Visualized Data/arenawise_card_win_loss.csv")

# Create master arena order and dropdown options
arena_order = sorted(list(set(grouped_df['arena'])), key=lambda x: int(x.split(' ')[1]))
troops_with_data = sorted(grouped_df['card_name'].unique())
troop_dropdown_options = [{'label': troop, 'value': troop} for troop in troops_with_data]

print("Data processing complete. Dash app is ready.")

# --- REUSABLE FIGURE FUNCTION ---
def create_troop_figure(selected_troop):
    """
    Filters the global grouped_df and returns a Plotly figure
    for the selected troop.
    """
    if not selected_troop:
        # Create a blank figure with the dark template
        return go.Figure(
            layout={
                "title": "Please select a troop", 
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)", # Transparent background
                "plot_bgcolor": "rgba(0,0,0,0)"  # Transparent background
            }
        )

    fig = go.Figure()
    df_troop = grouped_df[grouped_df['card_name'] == selected_troop]
    
    df_won = df_troop[df_troop['outcome'] == 'Won']
    df_lost = df_troop[df_troop['outcome'] == 'Lost']
    
    # Add Won Trace
    fig.add_trace(go.Bar(
        x=df_won['arena'], y=df_won['count'], name='Won',
        marker_color="#1343E1", 
        hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Won<br>Count: %{{y}}<extra></extra>",
        opacity=0.45
    ))
    # Add Lost Trace
    fig.add_trace(go.Bar(
        x=df_lost['arena'], y=df_lost['count'], name='Lost',
        marker_color="#EE0EC1", 
        hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Lost<br>Count: %{{y}}<extra></extra>",
        opacity=0.45
    ))
    
    fig.update_layout(
        title_text=f"{selected_troop} Usage: Win vs. Loss",
        xaxis_title="Arena",
        yaxis_title="Usage Count",
        barmode='overlay',
        template='plotly_dark',
        paper_bgcolor= "rgba(0,0,0,0)", # Transparent background
        plot_bgcolor= "rgba(0,0,0,0)"  # Transparent background
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
