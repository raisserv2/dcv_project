# pages/player_comparison.py
import dash
import pandas as pd
from dash import html, dcc, Input, Output, NoUpdate
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

dash.register_page(__name__, path="/troop", name="Troop Comparison")

TROOP_PATH = "../#2 Data Storage/Utils/troop_name.csv"
TROOP_STATS_PATH_NON_EVO = "../#2 Data Storage/Data Visualization Data/clash_royale_card_stats_non_evo.csv"
TROOP_STATS_PATH_EVO = "../#2 Data Storage/Data Visualization Data/clash_royale_card_stats_evo.csv"
df_troops_stats_non_evo = pd.read_csv(TROOP_STATS_PATH_NON_EVO)
df_troops_stats_evo = pd.read_csv(TROOP_STATS_PATH_EVO)
df_troops_name = pd.read_csv(TROOP_PATH)["Troop_name"]

grouped_df = pd.read_csv(
    "../#2 Data Storage/Visualized Data/arenawise_card_win_loss.csv"
)

# Create master arena order and dropdown options
arena_order = sorted(list(set(grouped_df["arena"])), key=lambda x: int(x.split(" ")[1]))
troops_with_data = sorted(grouped_df["card_name"].unique())
troop_dropdown_options = [
    {"label": troop, "value": troop} for troop in troops_with_data
]


# --- REUSABLE FIGURE FUNCTION ---
def create_troop_figure(selected_troop):
    """
    Filters the global grouped_df and returns a Plotly figure
    for the selected troop.
    """
    if not selected_troop:
        return go.Figure(layout={"title": "Please select a troop"})

    fig = go.Figure()
    df_troop = grouped_df[grouped_df["card_name"] == selected_troop]

    df_won = df_troop[df_troop["outcome"] == "Won"]
    df_lost = df_troop[df_troop["outcome"] == "Lost"]

    # Add Won Trace
    fig.add_trace(
        go.Bar(
            x=df_won["arena"],
            y=df_won["count"],
            name="Won",
            marker_color="#1343E1",
            hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Won<br>Count: %{{y}}<extra></extra>",
            opacity=0.45,
        )
    )
    # Add Lost Trace
    fig.add_trace(
        go.Bar(
            x=df_lost["arena"],
            y=df_lost["count"],
            name="Lost",
            marker_color="#EE0EC1",
            hovertemplate=f"Card: {selected_troop}<br>Arena: %{{x}}<br>Outcome: Lost<br>Count: %{{y}}<extra></extra>",
            opacity=0.45,
        )
    )

    fig.update_layout(
        title_text=f"{selected_troop} Usage: Win vs. Loss",
        xaxis_title="Arena",
        yaxis_title="Usage Count",
        barmode="overlay",
        template="plotly_dark",
    )

    # Apply sorting fix
    fig.update_xaxes(categoryorder="array", categoryarray=arena_order)

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
                                dbc.CardHeader("Troop Comparison"),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Troop:"),
                                        dcc.Dropdown(
                                            id="troop-dropdown-1",
                                            options=[
                                                {"label": troop, "value": troop}
                                                for troop in df_troops_name
                                            ],
                                            placeholder="Select a troop...",
                                            searchable=True,
                                            clearable=True,
                                            value=troops_with_data[0],
                                        ),
                                        html.Br(),
                                        html.Label("Evolution:"),
                                        dcc.RadioItems(
                                            id="evolution-selector-1",
                                            options=[
                                                {"label": "Normal", "value": "normal"},
                                                {"label": "Evolution", "value": "evo"},
                                            ],
                                            value="normal",
                                            inline=True,
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
                                dbc.CardHeader("Troop Comparison"),
                                dbc.CardBody(
                                    [
                                        html.Label("Select Troop:"),
                                        dcc.Dropdown(
                                            id="troop-dropdown-2",
                                            options=[
                                                {"label": troop, "value": troop}
                                                for troop in df_troops_name
                                            ],
                                            placeholder="Select a troop...",
                                            searchable=True,
                                            clearable=True,
                                            value=troops_with_data[1],
                                        ),
                                        html.Br(),
                                        html.Label("Evolution:"),
                                        dcc.RadioItems(
                                            id="evolution-selector-2",
                                            options=[
                                                {"label": "Normal", "value": "normal"},
                                                {"label": "Evolution", "value": "evo"},
                                            ],
                                            value="normal",
                                            inline=True,
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

            stat_items = [html.Li(f"{k}: {v}") for k, v in troop_data.items()]

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

            stat_items = [html.Li(f"{k}: {v}") for k, v in troop_data.items()]

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
        create_troop_figure(troop1),
        create_troop_figure(troop2),
    )
