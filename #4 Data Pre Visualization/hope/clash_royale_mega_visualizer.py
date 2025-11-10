import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
import pickle
import json
from collections import defaultdict
import ast

class ClashRoyaleMegaVisualizer:
    def __init__(self, card_db_path='card_database.csv', battle_data_path='clash_royale_data_separated.pkl'):
        """
        Initialize the mega visualizer with card database and battle data
        
        Args:
            card_db_path: Path to card_database.csv
            battle_data_path: Path to processed battle data pickle file
        """
        self.card_db = None
        self.battle_data = None
        self.evo_df = None
        self.non_evo_df = None
        self.combined_df = None
        
        self._load_data(card_db_path, battle_data_path)
    
    def _load_data(self, card_db_path, battle_data_path):
        """Load card database and battle data"""
        print("🚀 Loading data...")
        
        try:
            # Load card database
            self.card_db = pd.read_csv(card_db_path)
            print(f"✓ Loaded card database: {len(self.card_db)} cards")
            
            # Load battle data
            with open(battle_data_path, 'rb') as f:
                battle_data = pickle.load(f)
            
            # Create DataFrames for EVO and NON-EVO
            self.evo_df = pd.DataFrame({
                'card': list(battle_data['evo']['usage'].keys()),
                'usage_count': list(battle_data['evo']['usage'].values()),
                'win_count': [battle_data['evo']['wins'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
                'total_plays': [battle_data['evo']['total_plays'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
                'win_percentage': [battle_data['evo']['win_percentage'].get(card, 0) for card in battle_data['evo']['usage'].keys()],
                'card_type': 'EVO'
            })
            
            self.non_evo_df = pd.DataFrame({
                'card': list(battle_data['non_evo']['usage'].keys()),
                'usage_count': list(battle_data['non_evo']['usage'].values()),
                'win_count': [battle_data['non_evo']['wins'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
                'total_plays': [battle_data['non_evo']['total_plays'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
                'win_percentage': [battle_data['non_evo']['win_percentage'].get(card, 0) for card in battle_data['non_evo']['usage'].keys()],
                'card_type': 'NON_EVO'
            })
            
            # Merge with card database to get elixir cost and rarity
            self.evo_df = self.evo_df.merge(
                self.card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
                left_on='card', right_on='englishName', how='left'
            ).drop('englishName', axis=1)
            
            self.non_evo_df = self.non_evo_df.merge(
                self.card_db[['englishName', 'elixir_cost', 'rarity', 'is_evo']], 
                left_on='card', right_on='englishName', how='left'
            ).drop('englishName', axis=1)
            
            # Create combined DataFrame
            self.combined_df = pd.concat([self.evo_df, self.non_evo_df], ignore_index=True)
            
            print(f"✓ Loaded battle data: {len(self.combined_df)} card entries")
            print(f"  - EVO cards: {len(self.evo_df)}")
            print(f"  - NON-EVO cards: {len(self.non_evo_df)}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    # 1. EVO vs NON-EVO Performance Comparison
    def create_evo_comparison_bubble(self, min_plays=50):
        """Compare EVO vs NON-EVO performance"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        fig = px.scatter(df_filtered, x='usage_count', y='win_percentage',
                         color='card_type', size='total_plays', hover_name='card',
                         title='EVO vs NON-EVO Card Performance',
                         labels={'usage_count': 'Usage Count', 'win_percentage': 'Win Rate (%)'},
                         color_discrete_map={'EVO': '#FF6B6B', 'NON_EVO': '#4ECDC4'})
        
        fig.update_layout(height=600)
        return fig
    
    # 2. Elixir Cost Efficiency by EVO Status
    def create_elixir_efficiency_heatmap(self):
        """Heatmap showing efficiency by elixir cost and EVO status"""
        pivot_data = self.combined_df.groupby(['elixir_cost', 'card_type'])['win_percentage'].mean().reset_index()
        
        fig = px.density_heatmap(pivot_data, x='elixir_cost', y='card_type', z='win_percentage',
                                title='Win Rate by Elixir Cost and EVO Status',
                                color_continuous_scale='RdYlGn')
        return fig
    
    # 3. Rarity Performance by EVO Status
    def create_rarity_evo_comparison(self):
        """Compare performance across rarities and EVO status"""
        rarity_data = self.combined_df.groupby(['rarity', 'card_type']).agg({
            'win_percentage': 'mean',
            'usage_count': 'sum'
        }).reset_index()
        
        fig = px.bar(rarity_data, x='rarity', y='win_percentage', color='card_type',
                     title='Win Rate by Rarity and EVO Status',
                     barmode='group', color_discrete_map={'EVO': '#FF6B6B', 'NON_EVO': '#4ECDC4'})
        
        return fig
    
    # 4. EVO Impact Analysis
    def create_evo_impact_analysis(self):
        """Analyze the impact of evolution on card performance"""
        # Get cards that have both EVO and NON-EVO versions
        all_cards = set(self.evo_df['card']).union(set(self.non_evo_df['card']))
        comparison_data = []
        
        for card in all_cards:
            evo_data = self.evo_df[self.evo_df['card'] == card]
            non_evo_data = self.non_evo_df[self.non_evo_df['card'] == card]
            
            if len(evo_data) > 0 and len(non_evo_data) > 0:
                evo_win = evo_data.iloc[0]['win_percentage']
                non_evo_win = non_evo_data.iloc[0]['win_percentage']
                win_rate_change = evo_win - non_evo_win
                
                comparison_data.append({
                    'card': card,
                    'evo_win_rate': evo_win,
                    'non_evo_win_rate': non_evo_win,
                    'win_rate_change': win_rate_change,
                    'has_improvement': win_rate_change > 0
                })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        fig = px.bar(comparison_df, x='card', y='win_rate_change', color='has_improvement',
                     title='EVO Impact: Win Rate Change vs NON-EVO Version',
                     labels={'win_rate_change': 'Win Rate Change (%)', 'card': 'Card'},
                     color_discrete_map={True: '#4ECDC4', False: '#FF6B6B'})
        
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        return fig
    
    # 5. Card Performance Quadrant Analysis by EVO Status
    def create_evo_quadrant_analysis(self, min_plays=100):
        """Quadrant analysis separated by EVO status"""
        evo_filtered = self.evo_df[self.evo_df['total_plays'] >= min_plays]
        non_evo_filtered = self.non_evo_df[self.non_evo_df['total_plays'] >= min_plays]
        
        fig = make_subplots(rows=1, cols=2, 
                           subplot_titles=('EVO Cards', 'NON-EVO Cards'),
                           shared_xaxes=True, shared_yaxes=True)
        
        # EVO cards
        fig.add_trace(go.Scatter(
            x=evo_filtered['usage_count'], y=evo_filtered['win_percentage'],
            mode='markers+text', text=evo_filtered['card'],
            marker=dict(size=10, color='#FF6B6B'),
            name='EVO', showlegend=False
        ), row=1, col=1)
        
        # NON-EVO cards
        fig.add_trace(go.Scatter(
            x=non_evo_filtered['usage_count'], y=non_evo_filtered['win_percentage'],
            mode='markers+text', text=non_evo_filtered['card'],
            marker=dict(size=10, color='#4ECDC4'),
            name='NON-EVO', showlegend=False
        ), row=1, col=2)
        
        fig.update_layout(title_text="Card Performance Quadrant Analysis by EVO Status",
                         height=500)
        fig.update_xaxes(title_text="Usage Count")
        fig.update_yaxes(title_text="Win Rate (%)", row=1, col=1)
        
        return fig
    
    # 6. Elixir Cost vs Win Rate by EVO Status
    def create_elixir_win_rate_scatter(self, min_plays=50):
        """Scatter plot of elixir cost vs win rate colored by EVO status"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        fig = px.scatter(df_filtered, x='elixir_cost', y='win_percentage',
                         color='card_type', size='usage_count', hover_name='card',
                         title='Elixir Cost vs Win Rate by EVO Status',
                         labels={'elixir_cost': 'Elixir Cost', 'win_percentage': 'Win Rate (%)'},
                         color_discrete_map={'EVO': '#FF6B6B', 'NON_EVO': '#4ECDC4'})
        
        return fig
    
    # 7. Top Performing Cards by Category
    def create_top_performers_dashboard(self, min_plays=100):
        """Dashboard showing top performers in different categories"""
        categories = [
            ('Top EVO Cards', self.evo_df[self.evo_df['total_plays'] >= min_plays].nlargest(10, 'win_percentage')),
            ('Top NON-EVO Cards', self.non_evo_df[self.non_evo_df['total_plays'] >= min_plays].nlargest(10, 'win_percentage')),
            ('Most Used EVO', self.evo_df.nlargest(10, 'usage_count')),
            ('Most Used NON-EVO', self.non_evo_df.nlargest(10, 'usage_count'))
        ]
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=[cat[0] for cat in categories])
        
        for i, (title, data) in enumerate(categories):
            row = i // 2 + 1
            col = i % 2 + 1
            
            color = '#FF6B6B' if 'EVO' in title else '#4ECDC4'
            
            fig.add_trace(go.Bar(
                x=data['win_percentage'], y=data['card'], orientation='h',
                marker_color=color, name=title, showlegend=False
            ), row=row, col=col)
        
        fig.update_layout(height=800, title_text="Top Performing Cards Dashboard")
        return fig
    
    # 8. EVO Adoption Rate by Elixir Cost
    def create_evo_adoption_analysis(self):
        """Analyze EVO adoption rates across different elixir costs"""
        adoption_data = []
        
        for elixir in sorted(self.combined_df['elixir_cost'].unique()):
            if pd.isna(elixir):
                continue
                
            evo_cards = self.evo_df[self.evo_df['elixir_cost'] == elixir]
            non_evo_cards = self.non_evo_df[self.non_evo_df['elixir_cost'] == elixir]
            
            total_usage = evo_cards['usage_count'].sum() + non_evo_cards['usage_count'].sum()
            if total_usage > 0:
                evo_adoption_rate = (evo_cards['usage_count'].sum() / total_usage) * 100
                adoption_data.append({
                    'elixir_cost': elixir,
                    'evo_adoption_rate': evo_adoption_rate,
                    'total_cards': len(evo_cards) + len(non_evo_cards)
                })
        
        adoption_df = pd.DataFrame(adoption_data)
        
        fig = px.bar(adoption_df, x='elixir_cost', y='evo_adoption_rate',
                     title='EVO Card Adoption Rate by Elixir Cost',
                     labels={'elixir_cost': 'Elixir Cost', 'evo_adoption_rate': 'EVO Adoption Rate (%)'},
                     color='total_cards', color_continuous_scale='Viridis')
        
        return fig
    
    # 9. Comprehensive EVO vs NON-EVO Dashboard
    def create_comprehensive_evo_dashboard(self):
        """Comprehensive dashboard comparing EVO and NON-EVO cards"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Win Rate Distribution', 'Usage Distribution',
                'Elixir Cost Distribution', 'Rarity Distribution', 
                'Performance by Elixir Cost', 'Top 10 Cards by Win Rate'
            ),
            specs=[
                [{"type": "histogram"}, {"type": "histogram"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "box"}, {"type": "bar"}]
            ]
        )
        
        # 1. Win Rate Distribution
        fig.add_trace(go.Histogram(x=self.evo_df['win_percentage'], name='EVO', nbinsx=20, 
                                 marker_color='#FF6B6B', opacity=0.7), row=1, col=1)
        fig.add_trace(go.Histogram(x=self.non_evo_df['win_percentage'], name='NON-EVO', 
                                 nbinsx=20, marker_color='#4ECDC4', opacity=0.7), row=1, col=1)
        
        # 2. Usage Distribution
        fig.add_trace(go.Histogram(x=self.evo_df['usage_count'], name='EVO', nbinsx=20,
                                 marker_color='#FF6B6B', opacity=0.7, showlegend=False), row=1, col=2)
        fig.add_trace(go.Histogram(x=self.non_evo_df['usage_count'], name='NON-EVO',
                                 nbinsx=20, marker_color='#4ECDC4', opacity=0.7, showlegend=False), row=1, col=2)
        
        # 3. Elixir Cost Distribution
        elixir_evo = self.evo_df['elixir_cost'].value_counts().sort_index()
        elixir_non_evo = self.non_evo_df['elixir_cost'].value_counts().sort_index()
        
        fig.add_trace(go.Bar(x=elixir_evo.index, y=elixir_evo.values, name='EVO',
                           marker_color='#FF6B6B'), row=2, col=1)
        fig.add_trace(go.Bar(x=elixir_non_evo.index, y=elixir_non_evo.values, name='NON-EVO',
                           marker_color='#4ECDC4'), row=2, col=1)
        
        # 4. Rarity Distribution
        rarity_evo = self.evo_df['rarity'].value_counts()
        rarity_non_evo = self.non_evo_df['rarity'].value_counts()
        
        fig.add_trace(go.Bar(x=rarity_evo.index, y=rarity_evo.values, name='EVO',
                           marker_color='#FF6B6B', showlegend=False), row=2, col=2)
        fig.add_trace(go.Bar(x=rarity_non_evo.index, y=rarity_non_evo.values, name='NON-EVO',
                           marker_color='#4ECDC4', showlegend=False), row=2, col=2)
        
        # 5. Performance by Elixir Cost
        evo_by_elixir = self.evo_df.groupby('elixir_cost')['win_percentage'].mean()
        non_evo_by_elixir = self.non_evo_df.groupby('elixir_cost')['win_percentage'].mean()
        
        fig.add_trace(go.Box(y=self.evo_df['win_percentage'], x=self.evo_df['elixir_cost'],
                           name='EVO', marker_color='#FF6B6B'), row=3, col=1)
        fig.add_trace(go.Box(y=self.non_evo_df['win_percentage'], x=self.non_evo_df['elixir_cost'],
                           name='NON-EVO', marker_color='#4ECDC4'), row=3, col=1)
        
        # 6. Top 10 Cards by Win Rate
        top_evo = self.evo_df.nlargest(10, 'win_percentage')
        top_non_evo = self.non_evo_df.nlargest(10, 'win_percentage')
        
        fig.add_trace(go.Bar(y=top_evo['card'], x=top_evo['win_percentage'], orientation='h',
                           name='EVO', marker_color='#FF6B6B', showlegend=False), row=3, col=2)
        fig.add_trace(go.Bar(y=top_non_evo['card'], x=top_non_evo['win_percentage'], orientation='h',
                           name='NON-EVO', marker_color='#4ECDC4', showlegend=False), row=3, col=2)
        
        fig.update_layout(height=1200, title_text="Comprehensive EVO vs NON-EVO Analysis Dashboard")
        return fig

    def run_all_visualizations(self):
        """Run all visualizations and return a dictionary of figures"""
        print("🎨 Generating all visualizations...")
        
        visualizations = {
            "EVO Comparison Bubble": self.create_evo_comparison_bubble(),
            "Elixir Efficiency Heatmap": self.create_elixir_efficiency_heatmap(),
            "Rarity EVO Comparison": self.create_rarity_evo_comparison(),
            "EVO Impact Analysis": self.create_evo_impact_analysis(),
            "EVO Quadrant Analysis": self.create_evo_quadrant_analysis(),
            "Elixir Win Rate Scatter": self.create_elixir_win_rate_scatter(),
            "Top Performers Dashboard": self.create_top_performers_dashboard(),
            "EVO Adoption Analysis": self.create_evo_adoption_analysis(),
            "Comprehensive EVO Dashboard": self.create_comprehensive_evo_dashboard()
        }
        
        print("✅ All visualizations generated!")
        return visualizations

# Usage Instructions and Quick Start
def main():
    """
    MAIN EXECUTION - Run this to see all visualizations
    """
    print("=" * 70)
    print("🚀 CLASH ROYALE MEGA VISUALIZER")
    print("=" * 70)
    print("This script combines card database with battle data for advanced analysis")
    print("Prerequisites:")
    print("1. card_database.csv (from scraper)")
    print("2. clash_royale_data_separated.pkl (from data processor)")
    print("=" * 70)
    
    try:
        # Initialize visualizer
        visualizer = ClashRoyaleMegaVisualizer(
            card_db_path='card_database.csv',
            battle_data_path='clash_royale_data_separated.pkl'
        )
        
        # Generate all visualizations
        viz_dict = visualizer.run_all_visualizations()
        
        # Display one visualization at a time
        print("\n📊 Available Visualizations:")
        for i, (name, fig) in enumerate(viz_dict.items(), 1):
            print(f"{i}. {name}")
        
        print("\n🎯 Showing comprehensive dashboard first...")
        viz_dict["Comprehensive EVO Dashboard"].show()
        
        # Uncomment to show specific visualizations
        # viz_dict["EVO Impact Analysis"].show()
        # viz_dict["EVO Comparison Bubble"].show()
        
        return visualizer, viz_dict
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   - card_database.csv in the same directory")
        print("   - clash_royale_data_separated.pkl from the data processor")
        return None, None

if __name__ == "__main__":
    visualizer, viz_dict = main()
    
    if visualizer is not None:
        print("\n" + "=" * 70)
        print("✅ Analysis Complete!")
        print("💡 You can now access individual visualizations:")
        print("   visualizer.create_evo_comparison_bubble().show()")
        print("   visualizer.create_evo_impact_analysis().show()")
        print("   etc...")
        print("=" * 70)