import pandas as pd
import json
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display
from collections import defaultdict

def create_interactive_top_n_plot(json_path):
    """
    Loads card percentage data and creates an interactive plot
    with an Arena dropdown and a "Top N" slider.
    """
    
    # --- 1. Load the Data ---
    print(f"Loading data from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
        print("Please run the 'Process and Save' script first.")
        return
    
    # --- 2. Invert data from {Card: {Arena: %}} to {Arena: {Card: %}} ---
    arena_to_card_map = defaultdict(dict)
    all_arenas_int = range(2, 26)
    all_arenas_str = [str(i) for i in all_arenas_int]

    for card_name, arena_data in card_data.items():
        for arena_num_str in all_arenas_str:
            percent = arena_data.get(arena_num_str, 0.0)
            if percent > 0:
                arena_to_card_map[arena_num_str][card_name] = percent
    
    # --- 3. Create the Interactive Widgets ---
    
    # Arena selection "toggle bar"
    arena_dropdown = widgets.Dropdown(
        options=all_arenas_str,
        value='2',
        description='Select Arena:',
        style={'description_width': 'initial'}
    )
    
    # "Input number" for Top N cards (a slider is a great way to do this)
    top_n_slider = widgets.IntSlider(
        value=10,
        min=3,
        max=20,
        step=1,
        description='Show Top N Cards:',
        style={'description_width': 'initial'}
    )
    
    # --- 4. Create the Plotly FigureWidget ---
    # We initialize it with one empty bar plot
    fig = go.FigureWidget(data=[
        go.Bar(
            orientation='h', # Horizontal bar chart
            x=[], # x-axis is percentage (empty for now)
            y=[], # y-axis is card names (empty for now)
            marker_color='#1f77b4' # Plotly blue
        )
    ])
    
    # Apply our Tufte/Cleveland-style clean layout
    fig.update_layout(
        template='simple_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Usage Percentage (%)",
        yaxis_title="Card Name",
        yaxis=dict(autorange='reversed'), # Puts highest value at the top
        height=600,
        width=800
    )

    # --- 5. Define the "Update" Function ---
    # This function runs every time you change a widget
    def update_plot(change):
        # Get the new values from the widgets
        arena = arena_dropdown.value
        top_n = top_n_slider.value
        
        # Get the card data for the selected arena
        card_usage_map = arena_to_card_map.get(arena, {})
        
        # Sort cards by percentage and get the top N
        sorted_cards = sorted(card_usage_map.items(), key=lambda item: item[1], reverse=True)
        top_n_data = sorted_cards[:top_n]
        
        # Reverse for a horizontal bar chart (so highest is at the top)
        top_n_data.reverse()
        
        # Unzip the data into two lists
        cards = [item[0] for item in top_n_data]
        percentages = [item[1] for item in top_n_data]
        
        # --- Update the plot with new data ---
        # 'batch_update' is a fast way to update
        with fig.batch_update():
            fig.data[0].x = percentages
            fig.data[0].y = cards
            fig.layout.title = f"Top {top_n} Most Used Cards in Arena {arena}"
            # This line ensures the y-axis rescales to fit the new card names
            fig.layout.yaxis.autorange = True 

    # --- 6. Link the Widgets to the Update Function ---
    # Tell each widget to call 'update_plot' when its 'value' changes
    arena_dropdown.observe(update_plot, names='value')
    top_n_slider.observe(update_plot, names='value')
    
    # --- 7. Display the UI ---
    # HBox arranges the controls side-by-side
    controls = widgets.HBox([arena_dropdown, top_n_slider])
    display(controls)
    display(fig)
    
    # --- 8. Trigger the first plot ---
    update_plot(None)

# --- How to Run ---
if __name__ == "__main__":
    
    JSON_FILE = "card_percentage_dict.json"
    
    # Call the function in your notebook cell
    create_interactive_top_n_plot(JSON_FILE)