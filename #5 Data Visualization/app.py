# app.py
import dash
from dash import html
import dash_bootstrap_components as dbc

external = [
    "/assets/99_custom.css",
    "/assets/style.css"
]
# Initialize the app with Bootstrap theme
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external+[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
)
server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    brand="Battle Dashboard",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Troop A vs Troop B", href="/troop")),
        dbc.NavItem(dbc.NavLink("Arena Stats", href="/arena")),
        dbc.NavItem(dbc.NavLink("Builder", href="/builder")),
        dbc.NavItem(dbc.NavLink("Combos", href="/combined")),
        dbc.NavItem(dbc.NavLink("Evo", href="/evo")),
        dbc.NavItem(dbc.NavLink("Deck Archetypes", href="/deck")),
        dbc.NavItem(dbc.NavLink("Rarity Analysis", href="/rarity"))
    ],
)

# Main layout
app.layout = dbc.Container(
    [
        navbar,
        html.Br(),
        dash.page_container  # renders each registered page
    ],
    fluid=True,
)


if __name__ == "__main__":
    app.run(debug=True, port=8050)


# if __name__ == "__main__":
#     app.run( host ="0.0.0.0", debug=False, port=8050)
