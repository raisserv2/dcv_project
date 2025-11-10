import json
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_card_data():
    """Load the processed card data from files"""
    try:
        # Load from pickle for fastest access
        with open('clash_royale_data.pkl', 'rb') as f:
            data = pickle.load(f)
        return data
    except:
        # Fallback to JSON
        with open('card_usage_data.json', 'r') as f:
            usage = json.load(f)
        with open('card_win_data.json', 'r') as f:
            wins = json.load(f)
        with open('card_total_plays_data.json', 'r') as f:
            total_plays = json.load(f)
        with open('card_win_percentage_data.json', 'r') as f:
            win_pct = json.load(f)
        
        return {
            'usage': usage,
            'wins': wins, 
            'total_plays': total_plays,
            'win_percentage': win_pct
        }

def load_card_dataframe():
    """Load the comprehensive DataFrame"""
    try:
        return pd.read_pickle('clash_royale_card_stats.pkl')
    except:
        return pd.read_csv('clash_royale_card_stats.csv')

def create_win_rate_vs_usage_bubble(min_plays=100):
    """Create interactive bubble chart of win rate vs usage"""
    data = load_card_data()
    df = load_card_dataframe()
    
    # Filter cards with sufficient data
    df_filtered = df[df['total_plays'] >= min_plays].copy()
    
    fig = px.scatter(df_filtered, x='usage_count', y='win_percentage', 
                     size='total_plays', hover_name='card',
                     hover_data={'usage_count': True, 'win_percentage': ':.2f', 'total_plays': True},
                     title='Card Performance: Win Rate vs Usage',
                     labels={'usage_count': 'Usage Count (Unique Decks)', 
                            'win_percentage': 'Win Rate (%)',
                            'total_plays': 'Total Plays'},
                     size_max=40,
                     color='win_percentage',
                     color_continuous_scale='RdYlGn')
    
    # Add average lines
    avg_usage = df_filtered['usage_count'].mean()
    avg_win = df_filtered['win_percentage'].mean()
    
    fig.add_hline(y=avg_win, line_dash="dash", line_color="red", 
                  annotation_text=f"Avg Win Rate: {avg_win:.1f}%")
    fig.add_vline(x=avg_usage, line_dash="dash", line_color="red",
                  annotation_text=f"Avg Usage: {avg_usage:.1f}")
    
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode='closest',
        height=600
    )
    
    return fig

def create_usage_pie_chart(top_n=20):
    """Create pie chart of most used cards"""
    data = load_card_data()
    
    # Get top N cards by usage
    sorted_usage = sorted(data['usage'].items(), key=lambda x: x[1], reverse=True)[:top_n]
    cards = [item[0] for item in sorted_usage]
    counts = [item[1] for item in sorted_usage]
    
    fig = px.pie(names=cards, values=counts, 
                 title=f'Top {top_n} Most Used Cards',
                 hover_data={'value': True})
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_win_rate_bar_chart(min_plays=100, top_n=20):
    """Create bar chart of highest win rate cards"""
    df = load_card_dataframe()
    
    # Filter and sort
    df_filtered = df[df['total_plays'] >= min_plays]
    df_sorted = df_filtered.nlargest(top_n, 'win_percentage')
    
    fig = px.bar(df_sorted, x='card', y='win_percentage',
                 title=f'Top {top_n} Highest Win Rate Cards (min {min_plays} plays)',
                 labels={'win_percentage': 'Win Rate (%)', 'card': 'Card Name'},
                 color='win_percentage',
                 color_continuous_scale='RdYlGn')
    
    fig.update_layout(xaxis_tickangle=-45, height=500)
    
    return fig

def create_card_performance_dashboard():
    """Create a comprehensive dashboard of card performance"""
    data = load_card_data()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Win Rate vs Usage', 'Top 15 Most Used Cards', 
                       'Top 15 Highest Win Rates', 'Win Rate Distribution'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Win Rate vs Usage (scatter)
    df = load_card_dataframe()
    df_filtered = df[df['total_plays'] >= 100]
    
    scatter = px.scatter(df_filtered, x='usage_count', y='win_percentage', 
                        size='total_plays', hover_name='card')
    
    for trace in scatter.data:
        fig.add_trace(trace, row=1, col=1)
    
    # 2. Most Used Cards (bar)
    top_used = df.nlargest(15, 'usage_count')
    bar1 = px.bar(top_used, x='card', y='usage_count')
    
    for trace in bar1.data:
        fig.add_trace(trace, row=1, col=2)
    
    # 3. Highest Win Rates (bar)
    top_win = df[df['total_plays'] >= 100].nlargest(15, 'win_percentage')
    bar2 = px.bar(top_win, x='card', y='win_percentage')
    
    for trace in bar2.data:
        fig.add_trace(trace, row=2, col=1)
    
    # 4. Win Rate Distribution (histogram)
    hist = px.histogram(df, x='win_percentage', nbins=30)
    
    for trace in hist.data:
        fig.add_trace(trace, row=2, col=2)
    
    fig.update_layout(height=800, showlegend=False, 
                     title_text="Clash Royale Card Performance Dashboard")
    
    return fig

# Quick test function
def test_visualizations():
    """Test all visualizations"""
    print("Testing visualizations...")
    
    # Load data
    data = load_card_data()
    df = load_card_dataframe()
    
    print(f"Loaded data for {len(data['usage'])} unique cards")
    print(f"DataFrame shape: {df.shape}")
    
    # Create sample visualizations
    fig1 = create_win_rate_vs_usage_bubble()
    fig1.show()
    
    fig2 = create_usage_pie_chart()
    fig2.show()
    
    fig3 = create_win_rate_bar_chart()
    fig3.show()

if __name__ == "__main__":
    test_visualizations()