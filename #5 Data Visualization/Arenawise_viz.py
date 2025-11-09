import pandas as pd
import json
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# --- OPTION A: INTERACTIVE PLOTLY FUNCTION (All cards in one) ---
def plot_all_cards_interactive_smooth(all_data, output_html_path="card_usage_plot_smooth.html"):
    """
    Creates a single, interactive Plotly line chart for all cards,
    with smoother lines.
    """
    print("Generating smooth, clean interactive plot for all cards...")
    all_plot_data = []
    all_arenas = range(1, 25) 
    all_cards = sorted(list(all_data.keys()))
    
    for card_name in all_cards:
        card_data = all_data.get(card_name, {})
        for arena_num in all_arenas:
            arena_key = str(arena_num)
            percentage = card_data.get(arena_key, 0.0)
            all_plot_data.append({
                'card': card_name,
                'arena': arena_num,
                'percentage': percentage
            })

    if not all_plot_data:
        print("No data to plot.")
        return

    df = pd.DataFrame(all_plot_data)
    df['arena'] = df['arena'].astype(str)

    fig = go.Figure()

    for card_name in all_cards:
        df_card = df[df['card'] == card_name]
        fig.add_trace(
            go.Scatter(
                x=df_card['arena'],
                y=df_card['percentage'],
                name=card_name,
                mode='lines+markers', 
                line=dict(width=2, shape='spline', smoothing=0.8),
                marker=dict(size=6),
                hovertemplate=( 
                    f'<b>{card_name}</b><br>'
                    'Arena: %{x}<br>'
                    'Usage: %{y:.1f}%<extra></extra>' 
                ),
                visible=(card_name == all_cards[0]) # Show first card
            )
        )
        
    dropdown_buttons = []
    for i, card_name in enumerate(all_cards):
        visibility = [False] * len(all_cards)
        visibility[i] = True
        dropdown_buttons.append(
            dict(label=card_name, method="update",
                 args=[{"visible": visibility},
                       {"title": f'Usage Percentage for "{card_name}" (Arenas 1-24)'}])
        )

    fig.update_layout(
        template='simple_white', 
        plot_bgcolor='white', paper_bgcolor='white',
        title=dict(text=f'Usage Percentage for "{all_cards[0]}" (Arenas 1-24)', font=dict(size=16)),
        title_x=0.5, 
        xaxis_title="Arena Number", yaxis_title="Usage Percentage (%)",
        font=dict(family='Arial, sans-serif', color='black'), 
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12)),
        yaxis=dict(gridcolor='#EAEAEA', gridwidth=1, zeroline=False, tickfont=dict(size=12), rangemode='tozero'),
        updatemenus=[dict(active=0, buttons=dropdown_buttons, direction="down",
                          pad={"r": 10, "t": 10}, showactive=True, x=0.5,
                          xanchor="center", y=1.15, yanchor="top")],
        width=1000, height=600,
    )
    
    fig.write_html(output_html_path)
    fig.show()
    print(f"\nSuccessfully saved interactive plot to: {output_html_path}")

def main_load_and_plot():
    json_filename = "/Users/raghava/Downloads/card_percentage_dict.json"
    
    # --- LOAD THE DATA FROM THE JSON FILE ---
    print(f"Loading data from {json_filename}...")
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            # json.load reads the file and creates the dictionary
            card_percentage_dict = json.load(f)
        print(f"Successfully loaded {len(card_percentage_dict)} cards.")
    except FileNotFoundError:
        print(f"Error: File not found at {json_filename}")
        print("Please run Script 1 first to generate this file.")
        return
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return

    # --- NOW, CHOOSE YOUR VISUALIZATION ---

    # **CHOICE 1: Run the interactive Plotly chart (all-in-one)**
    plot_all_cards_interactive_smooth(card_percentage_dict)
    
    # **CHOICE 2: Run the Matplotlib plotter (one .png per card)**
    # (This will create a *lot* of files, so I've limited it to 10)
    
    # print("\n--- Generating individual card plots (Matplotlib) ---")
    # cards_to_plot = list(card_percentage_dict.keys())
    # for i, card in enumerate(cards_to_plot[:10]): # Plot the first 10 cards
    #     plot_card_percentage_updated(card_percentage_dict, card)
    # print("Done generating individual plots.")

if __name__ == "__main__":
    main_load_and_plot()