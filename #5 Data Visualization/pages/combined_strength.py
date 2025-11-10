import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# --- MODIFICATION: Added 'no_update' ---
from dash import Output, Input, no_update

dash.register_page(__name__, path="/combined", name="Combos")

INPUT_FILE = "../#2 Data Storage/Visualization Data/card_pair_data.csv"
TROOP_PATH = "../#2 Data Storage/Utils/troop_name.csv"

# --- MODIFICATION: Load and create the master options list ---
try:
    df_troops_name = pd.read_csv(TROOP_PATH)["Troop_name"]
    # Create the master list of options ONCE
    all_troop_options = [{"label": troop, "value": troop} for troop in df_troops_name]
    df_compared = pd.read_csv(INPUT_FILE)
except FileNotFoundError as e:
    print(f"Error loading data for combined_strength page: {e}")
    df_troops_name = pd.Series(["No Troops Found"])
    all_troop_options = [{"label": "No Troops Found", "value": "No Troops Found"}]
    df_compared = pd.DataFrame(columns=['card_1', 'card_2', 'usage_count', 'win_rate_percent'])
except pd.errors.EmptyDataError as e:
    print(f"Error: A data file was empty. {e}")
    df_troops_name = pd.Series(["No Troops Found"])
    all_troop_options = [{"label": "No Troops Found", "value": "No Troops Found"}]
    df_compared = pd.DataFrame(columns=['card_1', 'card_2', 'usage_count', 'win_rate_percent'])


def create_meta_map(csv_path):
    """
    Reads the card pair stats and generates an interactive
    scatter plot of Usage vs. Win Rate.
    """
    
    try:
        df = pd.read_csv(csv_path)
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Error creating meta map: {e}")
        return go.Figure(layout={"title": "Error: Could not load meta map data", "template": "plotly_dark"})
        
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
        line_color="white",
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
        template='plotly_dark',
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
    return fig

summary_metrics_card = dbc.Card([
    dbc.CardHeader("Summary Metrics"),
    dbc.CardBody([
        html.P("Usage Count:"),
        html.H4("—", id="total-strength", className="text-info"),
        html.P("Win Rate %:"),
        html.H4("—", id="avg-strength", className="text-success"),
        dbc.Button("Recalculate", color="primary", className="mt-2", id="recalc-button", n_clicks=0)
    ])
])

layout = dbc.Container(
    [
        html.H2("Troop Combinations Overview"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader("Troop 1"),
                        dbc.CardBody(
                            [
                                html.Label("Select Troop 1:"),
                                dcc.Dropdown(
                                    id="combo-dropdown-1",
                                    options=all_troop_options,
                                    placeholder="Select a troop...",
                                    searchable=True,
                                    clearable=True,
                                    value=df_troops_name.iloc[0] if not df_troops_name.empty else None,
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Troop 2"),
                        dbc.CardBody(
                            [
                                html.Label("Select Troop 2:"),
                                dcc.Dropdown(
                                    id="combo-dropdown-2",
                                    options=all_troop_options,
                                    placeholder="Select a troop...",
                                    searchable=True,
                                    clearable=True,
                                    value=df_troops_name.iloc[1] if len(df_troops_name) > 1 else None,
                                ),
                            ]
                        ),
                    ],
                    className="mt-3" 
                ),
                summary_metrics_card 
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop Combo Stats"),
                    dbc.CardBody([
                        dcc.Graph(
                            id={"type": "strength-chart", "index": 0}, 
                            figure={"data": [], "layout": {"title": "Combined Strength Chart"}}
                        )
                    ])
                ])
            ], md=8),
        ]), 
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id="meta-map-graph",
                    figure=create_meta_map(INPUT_FILE),
                    config={"displayModeBar": False}
                )
            ])
        ])
    ], 
    fluid=True
)


# --- START OF MODIFIED CALLBACKS ---

# Callback 1: Updates dropdown 2's OPTIONS when 1 changes
@dash.callback(
    Output("combo-dropdown-2", "options"),
    Input("combo-dropdown-1", "value"),
    prevent_initial_call=True
)
def update_dropdown_2_options(selected_troop_1):
    if not selected_troop_1:
        # If dropdown 1 was cleared, restore all options to dropdown 2
        return all_troop_options
        
    # Create new options list, excluding the selection from dropdown 1
    new_options_2 = [troop for troop in all_troop_options if troop['value'] != selected_troop_1]
    return new_options_2

# Callback 2: Updates dropdown 1's OPTIONS when 2 changes
@dash.callback(
    Output("combo-dropdown-1", "options"),
    Input("combo-dropdown-2", "value"),
    prevent_initial_call=True
)
def update_dropdown_1_options(selected_troop_2):
    if not selected_troop_2:
        # If dropdown 2 was cleared, restore all options to dropdown 1
        return all_troop_options

    # Create new options list, excluding the selection from dropdown 2
    new_options_1 = [troop for troop in all_troop_options if troop['value'] != selected_troop_2]
    return new_options_1

# --- END OF MODIFIED CALLBACKS ---


@dash.callback(
    Output("total-strength", "children"),
    Output("avg-strength", "children"),
    Output({"type": "strength-chart", "index": 0}, "figure"), 
    Input("combo-dropdown-1", "value"),
    Input("combo-dropdown-2", "value"),
    Input("recalc-button", "n_clicks") # Uncomment if you want to use the button
)
def update_strength(troop1, troop2, n_clicks):
    usuage_count = 0
    win_rate_percent = 0.0
    
    # --- MODIFICATION: Handle None or same-value inputs ---
    if not troop1 or not troop2:
        chart_title = "Please select two troops"
    elif troop1 == troop2:
        chart_title = "Please select two DIFFERENT troops"
    # --- END MODIFICATION ---
    else:
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

    # --- Dual Axis Chart Logic (Unchanged) ---
    strength_fig = go.Figure()

    strength_fig.add_trace(go.Bar(
        x=['Usage Count'], 
        y=[usuage_count],
        name='Usage Count',
        marker_color="#1167D7",
        text=[f"{usuage_count:,}"],
        textposition='auto',
        yaxis='y1' 
    ))
    
    strength_fig.add_trace(go.Bar(
        x=['Win Rate %'], 
        y=[win_rate_percent], 
        name='Win Rate %',
        marker_color="#18B480",
        text=[f"{win_rate_percent:.1f}%"],
        textposition='auto',
        yaxis='y2' 
    ))

    strength_fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        yaxis=dict(
            title="Usage Count",
            side="left",
            range=[0, max(usuage_count * 1.25, 10)], 
            title_font=dict(family="'Clash Bold', Arial, sans-serif"),
            tickfont=dict(family="'Clash Regular', Arial, sans-serif"),
            color="#1167D7" 
        ),
        yaxis2=dict(
            title="Win Rate %",
            side="right",
            overlaying="y", 
            range=[0, 100], 
            title_font=dict(family="'Clash Bold', Arial, sans-serif"),
            tickfont=dict(family="'Clash Regular', Arial, sans-serif"),
            color="#18B480" 
        ),
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
        legend=dict( 
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # Return updated metrics and figure
    return f"{usuage_count:,}", f"{win_rate_percent:.2f}%", strength_fig