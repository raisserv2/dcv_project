import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Set default theme for a cleaner look
pio.templates.default = "plotly_white"

def create_meta_map(csv_path, output_html_path="meta_map.html"):
    """
    Reads the card pair stats and generates an interactive
    scatter plot of Usage vs. Win Rate.
    """
    
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    if df.empty:
        print("The CSV file is empty. No plot generated.")
        return
        
    df['pair_name'] = df['card_1'] + " + " + df['card_2']

    print("Generating plot...")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df['usage_count'],
            y=df['win_rate_percent'],
            mode='markers',
            marker=dict(
                size=5,
                color=df['win_rate_percent'], # Color points by their win rate
                # --- COLORSCALE CHANGE HERE ---
                colorscale='Portland'
                 ,  # Changed from 'RdYlGn' to 'Portland'
                # Other good options: 'Bluered', 'Spectral', 'Plasma'
                # Or a custom one: [[0, 'red'], [0.5, 'white'], [1, 'green']]
                # ------------------------------
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

    fig.write_html(output_html_path)
    fig.show()
    
    print(f"\n--- SUCCESS ---")
    print(f"Interactive plot saved to: {output_html_path}")

# --- How to Run ---
if __name__ == "__main__":
    INPUT_FILE = "card_pair_data.csv"
    
    create_meta_map(INPUT_FILE)
