import dash
from dash import html,dcc, Input, Output
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
    brand_href="/",  # <-- Added this line to redirect to home
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Troop A vs Troop B", href="/troop")),
        dbc.NavItem(dbc.NavLink("Arena Stats", href="/arena")),
        dbc.NavItem(dbc.NavLink("Builder", href="/builder")),
        dbc.NavItem(dbc.NavLink("Combos", href="/combined")),
        dbc.NavItem(dbc.NavLink("Evo", href="/evo")),
        dbc.NavItem(dbc.NavLink("Rarity Analysis", href="/rarity")),
        dbc.NavItem(dbc.NavLink("Deck Archetypes", href="/deck")),
    ],
)

# Main layout
app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        navbar,
        html.Br(),
        dash.page_container
    ],
    fluid=True,
    id="main-app-container"  # <-- MAKE SURE THIS ID IS HERE
)


@app.callback(
    Output("main-app-container", "className"),
    Input("url", "pathname")
)
def update_page_class(pathname):
    # This function adds a CSS class to your main container
    # based on the URL, allowing you to style it in CSS.
    if pathname == "/evo":
        return "page-evo-background"
    elif pathname == "/deck":
        return "page-deck-background"
    elif pathname == "/troop":
        return "page-troop-background"
    elif pathname == "/builder":
        return "page-builder-background"
    elif pathname == "/rarity":
        return "page-rarity-background"
    elif pathname == "/combined":
        return "page-combined-background"
    elif pathname == "/arena":
        return "page-arena-background"
    
    
    else:
        # Default background for homepage ("/") or any other page
        return "page-default-background"

if __name__ == "__main__":
    app.run(debug=True, port=8050)


#if u want to deploy on local server uncomment below and comment above
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8050, debug=False)
