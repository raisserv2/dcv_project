# pages/player_comparison.py
import dash
import pandas as pd
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/troop", name="Troop Comparison")

TROOP_PATH = "C:/Users/Aseel/project/dcv_project/#2 Data Storage/Utils/troop_name.csv"


layout = dbc.Container(
    [
        html.H2("Troop A vs Troop B"),
        html.Hr(),

        # Troop Comparison Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop Comparison"),
                    dbc.CardBody([
                        html.Label("Select Troop:"),
                        dcc.Dropdown(
                            id="troop-dropdown",
                            options=[{"label": troop, "value": troop} for troop in pd.read_csv(TROOP_PATH)["Troop_name"]],
                            placeholder="Select a troop...",
                            searchable=True,
                            clearable=True,
                        ),
                        html.Br(),
                        html.Label("Evolution:"),
                        dcc.RadioItems(
                            id="evolution-selector",
                            options=[
                                {"label": "Normal", "value": "normal"},
                                {"label": "Evolution", "value": "evo"}
                            ],
                            value="normal",
                            inline=True
                        ),
                        html.Hr(),
                        html.Div(id="troop-info-1", className="mt-3")
                    ])
                ])
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Troop Comparison"),
                    dbc.CardBody([
                        html.Label("Select Troop:"),
                        dcc.Dropdown(
                            id="troop-dropdown",
                            options=[{"label": troop, "value": troop} for troop in pd.read_csv(TROOP_PATH)["Troop_name"]],
                            placeholder="Select a troop...",
                            searchable=True,
                            clearable=True,
                        ),
                        html.Br(),
                        html.Label("Evolution:"),
                        dcc.RadioItems(
                            id="evolution-selector",
                            options=[
                                {"label": "Normal", "value": "normal"},
                                {"label": "Evolution", "value": "evo"}
                            ],
                            value="normal",
                            inline=True
                        ),
                        html.Hr(),
                        html.Div(id="troop-info-2", className="mt-3")
                    ])
                ])
            ], md=6)
        ]),
        html.Hr(),
        
    ],
    fluid=True
)

# --- Callback ---
@dash.callback(
    Output("troop-info-1", "children"),
    Input("troop-dropdown", "value"),
    Input("evolution-selector", "value")
)
def update_troop_info(selected_troop, evolution_type):
    """Retrieve troop stats from DataFrame and display them."""
    if not selected_troop:
        return html.I("Select a troop to view its details.")

    # # Filter the troop info
    # troop_data = df_troops[df_troops["Troop"] == selected_troop]

    # # Example: If you have a column 'Evolution' to separate data
    # if "Evolution" in df_troops.columns:
    #     troop_data = troop_data[troop_data["Evolution"].str.lower() == evolution_type]

    # if troop_data.empty:
    #     return html.I("No data available for this troop and evolution type.")

    # # Convert troop stats to HTML list
    # stats_html = [
    #     html.Li(f"{col}: {val}") for col, val in troop_data.iloc[0].items()
    # ]

    # return dbc.Card([
    #     dbc.CardHeader(f"{selected_troop} ({evolution_type.capitalize()})"),
    #     dbc.CardBody(html.Ul(stats_html))
    # ])