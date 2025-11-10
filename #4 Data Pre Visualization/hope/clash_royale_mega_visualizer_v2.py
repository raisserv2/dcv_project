import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pickle
import json
from collections import defaultdict
import ast

class ClashRoyaleMegaVisualizerV2:
    def __init__(self, card_db_path='card_database.csv', battle_data_path='clash_royale_data_separated.pkl'):
        """
        Mega Visualizer V2 - All visualizations in one place
        """
        self.card_db = None
        self.battle_data = None
        self.evo_df = None
        self.non_evo_df = None
        self.combined_df = None
        
        self._load_data(card_db_path, battle_data_path)
        self._prepare_advanced_data()
    
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
            
            # Merge with card database
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
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def _prepare_advanced_data(self):
        """Prepare data for advanced visualizations"""
        # For archetype classification
        self.archetype_mapping = {
            'Beatdown': ['Golem', 'Lava Hound', 'Giant', 'Electro Giant', 'Royal Giant'],
            'Control': ['X-Bow', 'Mortar', 'Tesla', 'Bomb Tower', 'Inferno Tower'],
            'Cycle': ['Hog Rider', 'Miner', 'Wall Breakers', 'Skeletons', 'Ice Spirit'],
            'Spell Bait': ['Goblin Barrel', 'Princess', 'Dart Goblin', 'Goblin Gang'],
            'Bridge Spam': ['Bandit', 'Royal Ghost', 'Battle Ram', 'Dark Prince'],
            'Siege': ['X-Bow', 'Mortar', 'Bomb Tower'],
            'Spawner': ['Goblin Hut', 'Furnace', 'Barbarian Hut', 'Tombstone']
        }
        
        # Assign archetypes to cards
        self.combined_df['archetype'] = 'Utility'
        for archetype, cards in self.archetype_mapping.items():
            mask = self.combined_df['card'].isin(cards)
            self.combined_df.loc[mask, 'archetype'] = archetype

    # 1. Interactive Card Win Rate vs Usage Bubble Chart (with elixir cost as size)
    def create_win_rate_usage_bubble(self, min_plays=100):
        """Win Rate vs Usage with Elixir Cost as bubble size and custom rarity colors"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        # Custom color map for rarities
        rarity_colors = {
            "Common": "blue",
            "Rare": "orange",
            "Epic": "purple",
            "Legendary": "green",
            "Champion": "red"
        }
        
        fig = px.scatter(
            df_filtered,
            x='usage_count',
            y='win_percentage',
            size='elixir_cost',
            hover_name='card',
            color='rarity',
            size_max=30,
            title='Card Performance: Win Rate vs Usage (Bubble Size = Elixir Cost)',
            labels={'usage_count': 'Usage Count', 'win_percentage': 'Win Rate (%)'},
            color_discrete_map=rarity_colors
        )
        
        # Add average lines
        avg_usage = df_filtered['usage_count'].mean()
        avg_win = df_filtered['win_percentage'].mean()
        
        fig.add_hline(y=avg_win, line_dash="dash", line_color="red")
        fig.add_vline(x=avg_usage, line_dash="dash", line_color="red")
        
        fig.update_layout(height=600, xaxis_type="log")
        return fig


    # 2. Card Performance Heatmap by Elixir Cost
    def create_elixir_heatmap(self, min_plays=50):
        """Heatmap of performance by elixir cost"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        fig = px.density_heatmap(df_filtered, x='elixir_cost', y='win_percentage',
                                z='usage_count', histfunc="avg",
                                title='Card Performance Heatmap by Elixir Cost',
                                nbinsx=8, nbinsy=15,
                                color_continuous_scale='Viridis')
        
        return fig

    # 3. Interactive Deck Archetype Analysis
    def create_archetype_analysis(self):
        """Analyze deck archetypes performance"""
        archetype_stats = self.combined_df.groupby('archetype').agg({
            'win_percentage': 'mean',
            'usage_count': 'sum',
            'total_plays': 'sum',
            'card': 'count'
        }).reset_index()
        
        fig = px.scatter(archetype_stats, x='usage_count', y='win_percentage',
                         size='card', color='archetype', hover_name='archetype',
                         title='Deck Archetype Performance Analysis',
                         labels={'usage_count': 'Total Usage', 'win_percentage': 'Avg Win Rate (%)'})
        
        return fig

    # 4. Card Performance Radar Chart
    def create_card_radar_chart(self, selected_cards):
        """Radar chart comparing multiple cards"""
        selected_data = self.combined_df[self.combined_df['card'].isin(selected_cards)]
        
        if len(selected_data) == 0:
            print("No selected cards found in data")
            return None
            
        # Normalize metrics for radar chart
        metrics = ['usage_count', 'win_percentage', 'total_plays']
        normalized_data = []
        
        for card in selected_cards:
            card_data = self.combined_df[self.combined_df['card'] == card]
            if len(card_data) > 0:
                normalized_metrics = {}
                for metric in metrics:
                    max_val = self.combined_df[metric].max()
                    min_val = self.combined_df[metric].min()
                    val = card_data[metric].iloc[0]
                    normalized_metrics[metric] = ((val - min_val) / (max_val - min_val)) * 100
                normalized_metrics['card'] = card
                normalized_data.append(normalized_metrics)
        
        if not normalized_data:
            return None
            
        df_normalized = pd.DataFrame(normalized_data)
        
        fig = go.Figure()
        
        for _, row in df_normalized.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['usage_count'], row['win_percentage'], row['total_plays']],
                theta=['Usage', 'Win Rate', 'Total Plays'],
                fill='toself',
                name=row['card']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"Card Performance Radar: {', '.join(selected_cards)}"
        )
        
        return fig

    # 5. Meta Evolution Radar Chart (Simulated time periods)
    def create_meta_evolution_radar(self, time_periods=4):
        """Simulated meta evolution across time periods"""
        # Simulate time periods by splitting data
        archetypes = list(self.archetype_mapping.keys())
        periods_data = []
        
        for period in range(time_periods):
            # Simulate different meta strengths for each period
            np.random.seed(period)  # For reproducible results
            period_strengths = {}
            
            for archetype in archetypes:
                base_strength = np.random.normal(50, 15)
                period_strengths[archetype] = max(20, min(80, base_strength))
            
            for archetype, strength in period_strengths.items():
                periods_data.append({
                    'period': f'Period {period + 1}',
                    'archetype': archetype,
                    'strength': strength
                })
        
        df_periods = pd.DataFrame(periods_data)
        
        fig = go.Figure()
        
        for period in df_periods['period'].unique():
            period_data = df_periods[df_periods['period'] == period]
            fig.add_trace(go.Scatterpolar(
                r=period_data['strength'].tolist(),
                theta=period_data['archetype'].tolist(),
                fill='toself',
                name=period
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Meta Evolution: Archetype Strength Across Time Periods"
        )
        
        return fig

    # 6. Win Condition Heatmap by Elixir Cost
    def create_win_condition_heatmap(self, min_plays=100):
        """Heatmap focusing on win conditions"""
        win_conditions = ['Golem', 'Lava Hound', 'Giant', 'Royal Giant', 'Hog Rider', 
                         'Miner', 'X-Bow', 'Mortar', 'Balloon', 'Electro Giant']
        
        df_win_conditions = self.combined_df[
            (self.combined_df['card'].isin(win_conditions)) & 
            (self.combined_df['total_plays'] >= min_plays)
        ]
        
        fig = px.density_heatmap(df_win_conditions, x='elixir_cost', y='win_percentage',
                                z='usage_count', histfunc="avg",
                                title='Win Condition Performance by Elixir Cost',
                                color_continuous_scale='RdYlGn')
        
        # Add card labels
        for _, row in df_win_conditions.iterrows():
            fig.add_annotation(x=row['elixir_cost'], y=row['win_percentage'],
                             text=row['card'], showarrow=False, yshift=10)
        
        return fig

    # 7. Deck Archetype Sunburst Chart
    def create_archetype_sunburst(self):
        """Sunburst chart of archetypes and cards"""
        # Aggregate data for sunburst
        sunburst_data = []
        
        for archetype in self.combined_df['archetype'].unique():
            archetype_cards = self.combined_df[self.combined_df['archetype'] == archetype]
            total_usage = archetype_cards['usage_count'].sum()
            avg_win_rate = archetype_cards['win_percentage'].mean()
            
            # Archetype level
            sunburst_data.append({
                'ids': archetype,
                'labels': archetype,
                'parents': '',
                'values': total_usage,
                'win_rate': avg_win_rate
            })
            
            # Card level
            for _, card in archetype_cards.iterrows():
                sunburst_data.append({
                    'ids': f"{archetype}-{card['card']}",
                    'labels': card['card'],
                    'parents': archetype,
                    'values': card['usage_count'],
                    'win_rate': card['win_percentage']
                })
        
        df_sunburst = pd.DataFrame(sunburst_data)
        
        fig = px.sunburst(df_sunburst, path=['parents', 'labels'], values='values',
                         color='win_rate', color_continuous_scale='RdYlGn',
                         title='Deck Archetype Hierarchy and Performance')
        
        return fig

    # 8. Card Performance Parallel Coordinates
    def create_parallel_coordinates(self, min_plays=50):
        """Parallel coordinates plot for multi-dimensional analysis"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays].copy()
        
        # Select top cards for clarity
        top_cards = df_filtered.nlargest(30, 'usage_count')
        
        # Normalize metrics for parallel coordinates
        metrics = ['usage_count', 'win_percentage', 'total_plays', 'elixir_cost']
        for metric in metrics:
            top_cards[f'{metric}_norm'] = (top_cards[metric] - top_cards[metric].min()) / (top_cards[metric].max() - top_cards[metric].min())
        
        dimensions = []
        for metric in metrics:
            dimensions.append(dict(
                range=[0, 1],
                label=metric.replace('_', ' ').title(),
                values=top_cards[f'{metric}_norm']
            ))
        
        fig = go.Figure(data=go.Parcoords(
            line=dict(color=top_cards['win_percentage'],
                     colorscale='RdYlGn',
                     showscale=True),
            dimensions=dimensions,
            labelfont=dict(size=12),
            tickfont=dict(size=10)
        ))
        
        fig.update_layout(title='Multi-Dimensional Card Performance Analysis')
        return fig

    # 9. Matchup Matrix Heatmap
    def create_matchup_matrix(self, top_n=15):
        """Simulated matchup matrix between top cards"""
        top_cards = self.combined_df.nlargest(top_n, 'usage_count')['card'].tolist()
        
        # Create simulated matchup data (in real scenario, you'd calculate this from battle data)
        matchup_data = []
        for card1 in top_cards:
            row = {}
            for card2 in top_cards:
                if card1 == card2:
                    row[card2] = 50  # Draw against self
                else:
                    # Simulate some matchups (replace with real calculations)
                    base_win_rate = 50
                    card1_data = self.combined_df[self.combined_df['card'] == card1]
                    card2_data = self.combined_df[self.combined_df['card'] == card2]
                    
                    if len(card1_data) > 0 and len(card2_data) > 0:
                        card1_win = card1_data['win_percentage'].iloc[0]
                        card2_win = card2_data['win_percentage'].iloc[0]
                        win_rate = 50 + (card1_win - card2_win) / 2
                        row[card2] = max(30, min(70, win_rate))
                    else:
                        row[card2] = 50
            matchup_data.append(row)
        
        df_matchup = pd.DataFrame(matchup_data, index=top_cards)
        
        fig = px.imshow(df_matchup, x=top_cards, y=top_cards,
                       color_continuous_scale='RdYlGn', zmin=30, zmax=70,
                       title=f'Card Matchup Matrix (Top {top_n} Cards)',
                       labels=dict(color="Win Rate %"))
        
        fig.update_xaxes(tickangle=45)
        return fig

    # 10. Card Lifecycle Sankey Diagram
    def create_card_lifecycle_sankey(self):
        """Sankey diagram showing card popularity flow"""
        # Simulate card lifecycle stages
        stages = ['Low Usage', 'Medium Usage', 'High Usage', 'Meta']
        card_flow = []
        
        # Create simulated flow data
        for i, stage in enumerate(stages[:-1]):
            next_stage = stages[i + 1]
            flow_value = np.random.randint(10, 50)
            card_flow.append({
                'source': stage,
                'target': next_stage,
                'value': flow_value
            })
        
        # Create nodes and links for Sankey
        all_nodes = stages
        node_indices = {node: i for i, node in enumerate(all_nodes)}
        
        sources = [node_indices[flow['source']] for flow in card_flow]
        targets = [node_indices[flow['target']] for flow in card_flow]
        values = [flow['value'] for flow in card_flow]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5),
                     label=all_nodes),
            link=dict(source=sources, target=targets, value=values))
        ])
        
        fig.update_layout(title_text="Card Popularity Lifecycle Flow", font_size=10)
        return fig

    # 11. 3D Card Performance Scatter Plot
    def create_3d_scatter(self, min_plays=50):
        """3D scatter plot with usage, win rate, and elixir cost"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        fig = px.scatter_3d(df_filtered, x='usage_count', y='win_percentage', z='elixir_cost',
                           color='rarity', size='total_plays', hover_name='card',
                           title='3D Card Performance Analysis',
                           color_discrete_sequence=px.colors.qualitative.Bold)
        
        fig.update_layout(scene=dict(
            xaxis_title="Usage Count",
            yaxis_title="Win Rate %",
            zaxis_title="Elixir Cost"),
            margin=dict(l=0, r=0, b=0, t=30))
        
        return fig

    # 12. Card Performance Treemap
    def create_card_treemap(self, min_plays=30):
        """Treemap showing card performance"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        fig = px.treemap(df_filtered, path=['rarity', 'archetype', 'card'],
                        values='usage_count', color='win_percentage',
                        color_continuous_scale='RdYlGn',
                        title='Card Performance Treemap (Size=Usage, Color=Win Rate)')
        
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
        return fig

    # CREATIVE RARITY-BASED VISUALIZATIONS

    # 13. Rarity Performance Violin Plot
    def create_rarity_violin_plot(self):
        # Custom color map for rarities
        rarity_colors = {
            "Common": "blue",
            "Rare": "orange",
            "Epic": "purple",
            "Legendary": "green",
            "Champion": "red"
        }
        """Violin plot showing win rate distribution by rarity"""
        fig = px.violin(self.combined_df, x='rarity', y='win_percentage',
                       color='rarity', box=True, points="all",
                       title='Win Rate Distribution by Rarity',
                       color_discrete_map=rarity_colors)
        
        return fig

    # 14. Rarity Elixir Efficiency Scatter
    def create_rarity_elixir_efficiency(self, min_plays=50):
        """Scatter plot showing elixir efficiency by rarity"""
        df_filtered = self.combined_df[self.combined_df['total_plays'] >= min_plays]
        
        # Calculate efficiency (win rate per elixir)
        df_filtered['efficiency'] = df_filtered['win_percentage'] / df_filtered['elixir_cost']
        
        fig = px.scatter(df_filtered, x='elixir_cost', y='win_percentage',
                         color='rarity', size='usage_count', hover_name='card',
                         title='Elixir Efficiency by Rarity',
                         labels={'elixir_cost': 'Elixir Cost', 'win_percentage': 'Win Rate (%)'},
                         color_discrete_sequence=px.colors.qualitative.Bold)
        
        return fig

    # 15. Rarity Meta Share Donut Chart
    def create_rarity_meta_share(self):
        """Donut chart showing rarity distribution in the meta"""
        rarity_share = self.combined_df.groupby('rarity')['usage_count'].sum().reset_index()
        
        fig = px.pie(rarity_share, values='usage_count', names='rarity',
                     title='Rarity Distribution in Current Meta',
                     hole=0.4, color='rarity',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        return fig

    # 16. Rarity Evolution Impact
    def create_rarity_evolution_impact(self):
        """Show evolution impact across different rarities"""
        rarity_evo_impact = self.combined_df.groupby(['rarity', 'card_type']).agg({
            'win_percentage': 'mean',
            'usage_count': 'sum'
        }).reset_index()
        
        fig = px.bar(rarity_evo_impact, x='rarity', y='win_percentage', color='card_type',
                     title='Evolution Impact Across Rarities',
                     barmode='group', 
                     color_discrete_map={'EVO': '#FF6B6B', 'NON_EVO': '#4ECDC4'})
        
        return fig

    # 17. Rarity Performance Radar
    def create_rarity_performance_radar(self):
        """Radar chart comparing performance metrics across rarities"""
        rarity_metrics = self.combined_df.groupby('rarity').agg({
            'win_percentage': 'mean',
            'usage_count': 'mean',
            'total_plays': 'mean',
            'elixir_cost': 'mean'
        }).reset_index()
        
        # Normalize metrics
        metrics = ['win_percentage', 'usage_count', 'total_plays', 'elixir_cost']
        for metric in metrics:
            rarity_metrics[f'{metric}_norm'] = (rarity_metrics[metric] - rarity_metrics[metric].min()) / (rarity_metrics[metric].max() - rarity_metrics[metric].min()) * 100
        
        fig = go.Figure()
        
        for _, row in rarity_metrics.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['win_percentage_norm'], row['usage_count_norm'], 
                   row['total_plays_norm'], row['elixir_cost_norm']],
                theta=['Win Rate', 'Usage', 'Total Plays', 'Elixir Cost'],
                fill='toself',
                name=row['rarity']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Rarity Performance Comparison"
        )
        
        return fig

    def run_all_visualizations(self):
        """Run all visualizations and return a dictionary of figures"""
        print("🎨 Generating all visualizations...")
        
        visualizations = {
            # Original requested visualizations
            "Win Rate vs Usage Bubble": self.create_win_rate_usage_bubble(),
            "Elixir Heatmap": self.create_elixir_heatmap(),
            "Archetype Analysis": self.create_archetype_analysis(),
            "Card Radar": self.create_card_radar_chart(['Knight', 'Archers', 'Musketeer', 'Valkyrie']),
            "Meta Evolution Radar": self.create_meta_evolution_radar(),
            "Win Condition Heatmap": self.create_win_condition_heatmap(),
            "Archetype Sunburst": self.create_archetype_sunburst(),
            "Parallel Coordinates": self.create_parallel_coordinates(),
            "Matchup Matrix": self.create_matchup_matrix(),
            "Card Lifecycle Sankey": self.create_card_lifecycle_sankey(),
            "3D Scatter": self.create_3d_scatter(),
            "Card Treemap": self.create_card_treemap(),
            
            # Creative rarity-based visualizations
            "Rarity Violin Plot": self.create_rarity_violin_plot(),
            "Rarity Elixir Efficiency": self.create_rarity_elixir_efficiency(),
            "Rarity Meta Share": self.create_rarity_meta_share(),
            "Rarity Evolution Impact": self.create_rarity_evolution_impact(),
            "Rarity Performance Radar": self.create_rarity_performance_radar(),
        }
        
        print("✅ All visualizations generated!")
        return visualizations

# Quick Start Function
def main():
    """
    MAIN EXECUTION - Run this to see all visualizations
    """
    print("=" * 70)
    print("🚀 CLASH ROYALE MEGA VISUALIZER V2")
    print("=" * 70)
    print("All-in-one visualization suite with 17 advanced charts!")
    print("Prerequisites:")
    print("1. card_database.csv")
    print("2. clash_royale_data_separated.pkl")
    print("=" * 70)
    
    try:
        visualizer = ClashRoyaleMegaVisualizerV2()
        viz_dict = visualizer.run_all_visualizations()
        
        print("\n📊 Available Visualizations (17 total):")
        for i, (name, fig) in enumerate(viz_dict.items(), 1):
            print(f"{i:2d}. {name}")
        
        print("\n🎯 Showing comprehensive dashboard...")
        # Show a key visualization first
        viz_dict["Win Rate vs Usage Bubble"].show()
        
        return visualizer, viz_dict
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    visualizer, viz_dict = main()
    
    if visualizer is not None:
        print("\n" + "=" * 70)
        print("✅ Analysis Complete!")
        print("💡 Access individual visualizations:")
        print("   visualizer.create_win_rate_usage_bubble().show()")
        print("   visualizer.create_rarity_violin_plot().show()")
        print("   etc...")
        print("=" * 70)