# pages/combined_strength.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from dash import Output, Input
dash.register_page(__name__, path="/combined", name="Combined Strength")

INPUT_FILE = "../#2 Data Storage/Data Visualization Data/card_pair_data.csv"
TROOP_PATH = "../#2 Data Storage/Utils/troop_name.csv"
df_troops_name = pd.read_csv(TROOP_PATH)["Troop_name"]

df_compared = pd.read_csv(INPUT_FILE)

def create_meta_map(csv_path):
    """
    Reads the card pair stats and generates an interactive
    scatter plot of Usage vs. Win Rate.
    """
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return None # Return None if file is missing
        
    df['pair_name'] = df['card_1'] + " + " + df['card_2']

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df['usage_count'],
            y=df['win_rate_percent'],
            mode='markers',
            marker=dict(
                size=5,
                color=df['win_rate_percent'], 
                colorscale='Bluered',
                showscale=True,
                colorbar=dict(title='Win Rate %')
            ),
            hovertemplate=(
                f"<b>Pair:</b> %{{customdata[0]}}<br>"
                f"<b>Usage:</b> %{{x:,}}<br>"
                f"<b>Win Rate:</b> %{{y:.1f}}%"
                "<extra></extra>"
            ),
            customdata=df[['pair_name']]
        )
    )

    fig.add_hline(
        y=50.0,
        line_dash="dash",
        line_color="black",
        annotation_text="50% Win Rate",
        annotation_position="bottom right"
    )

    fig.update_layout(
        title="Card Pair Meta Map (Usage vs. Win Rate)",
        xaxis_title="Popularity (Usage Count)",
        yaxis_title="Effectiveness (Win Rate %)",
        xaxis_type="log",
        yaxis=dict(
            range=[35, 65]
        ),
        hovermode="closest",
        height=700,
        template='plotly_white'
    )
    return fig

# --- FIX 3: Updated Labels for Clarity ---
summary_metrics_card = dbc.Card([
    dbc.CardHeader("Summary Metrics"),
    dbc.CardBody([
        html.P("Usage Count:"), # <-- RENAMED
        html.H4("—", id="total-strength", className="text-success"),
        html.P("Win Rate %:"), # <-- RENAMED
        html.H4("—", id="avg-strength", className="text-info"),
        # Note: The "Recalculate" button doesn't have an Input/State in any callback
        # You may want to wire this up if it's supposed to do something.
        dbc.Button("Recalculate", color="primary", className="mt-2", id="recalc-button", n_clicks=0)
    ])
])

layout = dbc.Container(
    [
        html.H2("Combined Strength Overview"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader("Troop Comparison"),
                        dbc.CardBody(
                            [
                                html.Label("Select Combined Troop 1:"),
                                dcc.Dropdown(
                                    id="troop-dropdown-1",
                                    options=[
                                        {"label": troop, "value": troop}
                                        for troop in df_troops_name
                                    ],
                                    placeholder="Select a troop...",
                                    searchable=True,
                                    clearable=True,
                                    value=df_troops_name[0],
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Troop Comparison"),
                        dbc.CardBody(
                            [
                                html.Label("Select Combined Troop 2:"),
                                dcc.Dropdown(
                                    id="troop-dropdown-2",
                                    options=[
                                        {"label": troop, "value": troop}
                                        for troop in df_troops_name
                                    ],
                                    placeholder="Select a troop...",
                                    searchable=True,
                                    clearable=True,
                                    value=df_troops_name[0], # Consider setting a different default?
                                ),
                            ]
                        ),
                    ],
                    className="mt-3" # Added margin top for spacing
                ),
                summary_metrics_card # <-- Using the variable from above
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Strength Distribution"),
                    dbc.CardBody([
                        dcc.Graph(
                            # --- FIX 1: Added matching ID ---
                            id={"type": "strength-chart", "index": 0}, 
                            figure={"data": [], "layout": {"title": "Combined Strength Chart"}}
                        )
                    ])
                ])
            ], md=8),
        ]), # <-- This row was closed prematurely in your code, fixed it.
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id="meta-map-graph",
                    # --- FIX 4: Figure is loaded here, no callback needed ---
                    figure=create_meta_map(INPUT_FILE) if create_meta_map(INPUT_FILE) else go.Figure(layout={"title": "No data available"}),
                    config={"displayModeBar": False}
                )
            ])
        ])
    ], 
    fluid=True
)

# --- FIX 4: Removed the redundant update_meta_map callback ---
# (It's no longer needed)


@dash.callback(
    Output("total-strength", "children"),
    Output("avg-strength", "children"),
    Output({"type": "strength-chart", "index": 0}, "figure"), 
    Input("troop-dropdown-1", "value"),
    Input("troop-dropdown-2", "value"),
    # Add n_clicks from the button if you want it to trigger the callback
    # Input("recalc-button", "n_clicks") 
)
def update_strength(troop1, troop2): #, n_clicks):
    usuage_count = 0
    win_rate_percent = 0.0
    chart_title = "Combined Strength Distribution"

    if troop1 and troop2:
        filtered_df = df_compared[
            ((df_compared["card_1"] == troop1) & (df_compared["card_2"] == troop2)) |
            ((df_compared["card_1"] == troop2) & (df_compared["card_2"] == troop1))
        ]
        if not filtered_df.empty:
            usuage_count = filtered_df.iloc[0]["usage_count"]
            win_rate_percent = filtered_df.iloc[0]["win_rate_percent"]
            chart_title = f"Metrics for {troop1} + {troop2}"
        else:
            chart_title = f"No data for {troop1} + {troop2}"

    # --- FIX 2: Updated chart logic ---
    strength_fig = go.Figure()
    strength_fig.add_trace(go.Bar(
        x=['Usage Count', 'Win Rate %'],
        y=[usuage_count, win_rate_percent],
        marker_color=["#1343E1", "#E11343"],
        text=[f"{usuage_count:,}", f"{win_rate_percent:.1f}%"],
        textposition='auto'
    ))
    strength_fig.update_layout(
        title=chart_title,
        yaxis_title="Value",
        template="plotly_white",
        yaxis=dict(range=[0, max(usuage_count * 1.2, win_rate_percent * 1.2, 100)]) # Dynamic y-axis
    )
    
    # --- FIX 5: Removed unused meta_fig variable ---
    
    # Return updated metrics and figure
    return f"{usuage_count:,}", f"{win_rate_percent:.2f}%", strength_fig