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
        dbc.NavItem(dbc.NavLink("Arena Comparison", href="/arena")),
        dbc.NavItem(dbc.NavLink("Custom Builder", href="/builder")),
        dbc.NavItem(dbc.NavLink("Combined Strength", href="/combined")),
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
    app.run(debug=True,port=1111)
