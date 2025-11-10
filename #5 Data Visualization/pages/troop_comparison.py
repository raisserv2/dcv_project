# pages/player_comparison.py
import dash
import pandas as pd
from dash import html, dcc, Input, Output, NoUpdate
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

dash.register_page(__name__, path="/troop", name="Troop Comparison")

TROOP_PATH = "../#2 Data Storage/Utils/troop_name.csv"
TROOP_STATS_PATH_NON_EVO = "../#2 Data Storage/Visualization Data/clash_royale_card_stats_non_evo.csv"
TROOP_STATS_PATH_EVO = "../#2 Data Storage/Visualization Data/clash_royale_card_stats_evo.csv"
WIN_LOSS_PATH = "../#2 Data Storage/Visualization Data/arenawise_card_win_loss.csv"

# --- Load Data ---
try:
    df_troops_stats_non_evo = pd.read_csv(TROOP_STATS_PATH_NON_EVO)
    df_troops_stats_evo = pd.read_csv(TROOP_STATS_PATH_EVO)
    df_troops = pd.read_csv(TROOP_PATH)
    df_troops_name = df_troops["Troop_name"]
    # Create the lookup map: {'Knight': 1, 'Archers': 1, 'Goblins': 0}
    evo_lookup_map = pd.Series(df_troops.Evolution.values, index=df_troops.Troop_name).to_dict()
    
    grouped_df = pd.read_csv(WIN_LOSS_PATH)
    
    # --- Data Prep ---
    # Convert "Arena 1" to "1"
    grouped_df["arena"] = grouped_df["arena"].str.replace("Arena ", "")
    # Create master arena order
    arena_order = sorted(list(set(grouped_df["arena"])), key=lambda x: int(x))
    # Create dropdown options
    troops_with_data = sorted(grouped_df["card_name"].unique())
    troop_dropdown_options = [
        {"label": troop, "value": troop} for troop in troops_with_data
    ]
except FileNotFoundError as e:
    print(f"Error loading data: {e}")
    # Create empty dataframes/lists as fallbacks
    df_troops_stats_non_evo = pd.DataFrame()
    df_troops_stats_evo = pd.DataFrame()
    df_troops_name = pd.Series(["No Troops Found"])
    grouped_df = pd.DataFrame(columns=['arena', 'card_name', 'outcome', 'evo', 'count'])
    arena_order = []
    troops_with_data = ["No Data"]
    troop_dropdown_options = []


# --- REUSABLE FIGURE FUNCTION ---
def create_troop_figure(selected_troop, evo_type):
    """
    Filters the global grouped_df and returns a Plotly figure
    for the selected troop AND evolution status.
    """
    if not selected_troop:
        return go.Figure(
            layout={
                "title": "Please select a troop", 
                "template": "plotly_dark",
                "font": {"family": "'Clash Regular', Arial, sans-serif"},
                "xaxis":{"showgrid": False, "visible": False},
                "yaxis":{"showgrid": False, "visible": False},
            }
        )
    
    # Map the radio button value to the 'evo' column value (0 or 1)
    evo_filter = 1 if evo_type == "evo" else 0
    
    # Filter by both card name AND evolution status
    df_troop = grouped_df[
        (grouped_df["card_name"] == selected_troop) &
        (grouped_df["evo"] == evo_filter)
    ]
    
    if df_troop.empty:
        title_message = f"No {evo_type.capitalize()} data found for {selected_troop}"
        # Return a blank figure with a message
        return go.Figure(
            layout={
                "title": title_message, 
                "template": "plotly_dark",
                "font": {"family": "'Clash Regular', Arial, sans-serif"},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "xaxis":{"showgrid": False, "visible": False},
                "yaxis":{"showgrid": False, "visible": False},
            }
        )
    
    df_won = df_troop[df_troop["outcome"] == "Won"]
    df_lost = df_troop[df_troop["outcome"] == "Lost"]

    fig = go.Figure()

    # Add Won Trace
    fig.add_trace(
        go.Bar(
            x=df_won["arena"],
            y=df_won["count"],
            name="Won",
            marker_color="#1343E1",
            # Updated hovertemplate
            hovertemplate=f"Card: {selected_troop} ({evo_type.capitalize()})<br>Arena: %{{x}}<br>Outcome: Won<br>Count: %{{y}}<extra></extra>",
            opacity=1,
        )
    )
    # Add Lost Trace
    fig.add_trace(
        go.Bar(
            x=df_lost["arena"],
            y=df_lost["count"],
            name="Lost",
            marker_color="#E61C23",
            # Updated hovertemplate
            hovertemplate=f"Card: {selected_troop} ({evo_type.capitalize()})<br>Arena: %{{x}}<br>Outcome: Lost<br>Count: %{{y}}<extra></extra>",
            opacity=1,
        )
    )

    fig.update_layout(
        # Updated title
        title_text=f"{selected_troop} ({evo_type.capitalize()}) Usage: Win vs. Loss",
        xaxis_title="Arena",
        yaxis_title="Usage Count",
        barmode="group", # 'relative' is good for stacked, 'overlay' is what you had
        paper_bgcolor= "rgba(0,0,0,0)",
        plot_bgcolor= "rgba(0,0,0,0)", 
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

    # Apply sorting fix
    fig.update_xaxes(categoryorder="array", categoryarray=arena_order, tickmode='array', tickvals=arena_order, tickangle=-60)

    return fig

layout = dbc.Container(
    [
        html.H2("Troop A vs Troop B"),
        html.Hr(),
        # Troop Comparison Section
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Troop 1"),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Troop:"),
                                        dcc.Dropdown(
                                            id="troop-dropdown-1",
                                            options=troop_dropdown_options, # type: ignore
                                            placeholder="Select a troop...",
                                            searchable=True,
                                            clearable=True,
                                            value=troops_with_data[0],
                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="evolution-container-1",
                                            style={'display': 'none'}, # Hide by default
                                            children=[
                                                dcc.RadioItems(
                                                    id="evolution-selector-1",
                                                    options=[
                                                        {"label": "Normal", "value": "normal"},
                                                        {"label": "Evolution", "value": "evo"},
                                                    ],
                                                    value="normal",
                                                    inline=True,
                                                    className="dbc"
                                                ),
                                            ]
                                        ),
                                        html.Hr(),
                                        html.Div(id="troop-info-1", className="mt-3"),
                                        html.Hr(),
                                        dcc.Graph(id="troop-1-figure"),
                                    ]
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Troop 2"),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Troop:"),
                                        dcc.Dropdown(
                                            id="troop-dropdown-2",
                                            options=troop_dropdown_options, # type: ignore
                                            placeholder="Select a troop...",
                                            searchable=True,
                                            clearable=True,
                                            value=troops_with_data[1],
                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="evolution-container-2",
                                            style={'display': 'none'}, # Hide by default
                                            children=[
                                                dcc.RadioItems(
                                                    id="evolution-selector-2",
                                                    options=[
                                                        {"label": "Normal", "value": "normal"},
                                                        {"label": "Evolution", "value": "evo"},
                                                    ],
                                                    value="normal",
                                                    inline=True,
                                                    className="dbc"
                                                ),
                                            ]
                                        ),
                                        html.Hr(),
                                        html.Div(id="troop-info-2", className="mt-3"),
                                        html.Hr(),
                                        dcc.Graph(id="troop-2-figure"),
                                    ]
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ]
        ),
        html.Hr(),
    ],
    fluid=True,
)

# --- NEW CALLBACK 1: Show/Hide Evo Radio for Troop 1 ---
@dash.callback(
    Output("evolution-container-1", "style"),
    Output("evolution-selector-1", "value"),
    Input("troop-dropdown-1", "value")
)
def toggle_evolution_radio_1(selected_troop):
    if selected_troop and evo_lookup_map.get(selected_troop) == 1:
        # If troop exists and has evo (1), show the radio buttons
        return {'display': 'block'}, dash.no_update # Keep current value
    else:
        # If no troop selected or troop has no evo (0), hide and reset
        return {'display': 'none'}, "normal" 

# --- NEW CALLBACK 2: Show/Hide Evo Radio for Troop 2 ---
@dash.callback(
    Output("evolution-container-2", "style"),
    Output("evolution-selector-2", "value"),
    Input("troop-dropdown-2", "value")
)
def toggle_evolution_radio_2(selected_troop):
    if selected_troop and evo_lookup_map.get(selected_troop) == 1:
        # If troop exists and has evo (1), show the radio buttons
        return {'display': 'block'}, dash.no_update # Keep current value
    else:
        # If no troop selected or troop has no evo (0), hide and reset
        return {'display': 'none'}, "normal"

@dash.callback(
    Output("troop-info-1", "children"),
    Output("troop-info-2", "children"),
    Output("troop-1-figure", "figure"),
    Output("troop-2-figure", "figure"),
    Input("troop-dropdown-1", "value"),
    Input("evolution-selector-1", "value"),
    Input("troop-dropdown-2", "value"),
    Input("evolution-selector-2", "value"),
)
def update_troop_cards(troop1, evo1, troop2, evo2):
    def render_troop_card(selected_troop, evo_type):
        if not selected_troop:
            return html.I("Select a troop to view details.")
        if evo_type == "normal":
            troop_data = df_troops_stats_non_evo[df_troops_stats_non_evo["card"] == selected_troop]

            if troop_data.empty:
                return html.I("No data found for this troop configuration.")

            troop_data = troop_data.iloc[0].to_dict()

            img_component = None
            if "card" in troop_data and pd.notna(troop_data["card"]):
                img_path = f"../assets/2_icon_scrpaing/card_icons/{troop_data['card']}.webp"
                if troop_data['card'] == "Mini P.E.K.K.A":
                    img_path = "../assets/2_icon_scrpaing/card_icons/Mini PEKKA.webp"
                if troop_data['card'] == "P.E.K.K.A":
                    img_path = "../assets/2_icon_scrpaing/card_icons/PEKKA.webp"
                

                img_component = html.Img(
                    id=f"img-{selected_troop}-{evo_type}",
                    src=img_path,
                    style={
                        "width": "100%",
                        "maxHeight": "220px",
                        "objectFit": "contain",
                        "marginBottom": "10px",
                    },
                )

            stat_items = []
            for k,v in troop_data.items():
                k = k.replace("_", " ").capitalize()
                if v == "NON_EVO":
                    v = "Normal"
                stat_items.append(html.Li(f"{k}: {v}")) 

            # Single component: card containing image and stats, wrapped in Loading
            card = dbc.Card(
                [
                    dbc.CardHeader(f"{selected_troop} ({evo_type.capitalize()})"),
                    dbc.CardBody(
                        [
                            img_component if img_component is not None else html.Div(),
                            html.Ul(stat_items),
                        ]
                    ),
                ]
            )
            return dcc.Loading(children=card)
        else:  # evo_type == "evo"
            troop_data = df_troops_stats_evo[df_troops_stats_evo["card"] == selected_troop]

            if troop_data.empty:
                return html.I("No data found for this troop configuration.")

            troop_data = troop_data.iloc[0].to_dict()

            img_component = None
            if "card" in troop_data and pd.notna(troop_data["card"]):
                img_path = f"../assets/2_icon_scrpaing/evo_card_icons/{troop_data['card']}.webp"
         
                if troop_data['card'] == "P.E.K.K.A":
                    img_path = f"../assets/2_icon_scrpaing/evo_card_icons/PEKKA.webp"
                img_component = html.Img(
                    id=f"img-{selected_troop}-{evo_type}",
                    src=img_path,
                    style={
                        "width": "100%",
                        "maxHeight": "220px",
                        "objectFit": "contain",
                        "marginBottom": "10px",
                    },
                )

            stat_items = []
            for k,v in troop_data.items():
                k = k.replace("_", " ").capitalize()
                if v == "EVO":
                    v = "Evolution"
                stat_items.append(html.Li(f"{k}: {v}")) 

            # Single component: card containing image and stats, wrapped in Loading
            card = dbc.Card(
                [
                    dbc.CardHeader(f"{selected_troop} ({evo_type.capitalize()})"),
                    dbc.CardBody(
                        [
                            img_component if img_component is not None else html.Div(),
                            html.Ul(stat_items),
                        ]
                    ),
                ]
            )
            return dcc.Loading(children=card)
    

    return (
        render_troop_card(troop1, evo1),
        render_troop_card(troop2, evo2),
        create_troop_figure(troop1, evo1),
        create_troop_figure(troop2, evo2),
    )
