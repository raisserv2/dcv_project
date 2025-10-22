import requests
import time
import json
import random
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import deque, defaultdict
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime, timedelta

class UniformClashRoyaleScraper:
    def __init__(self, max_workers: int = 5):
        self.base_url = "https://stats-royale-api-js-beta-z2msk5bu3q-uk.a.run.app"
        self.headers = {
            'authority': 'stats-royale-api-js-beta-z2msk5bu3q-uk.a.run.app',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://statsroyale.com',
            'priority': 'u=1, i',
            'referer': 'https://statsroyale.com/',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_workers = max_workers
        self.visited_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.quota_lock = threading.Lock()
        
    def setup_quota_system(self, total_quota: int = 50000, strategy: str = "arena_based"):
        """
        Setup quota system for uniform distribution
        Strategies: "arena_based", "bucket_based", "hybrid"
        """
        self.total_quota = total_quota
        self.strategy = strategy
        
        if strategy == "arena_based":
            # 24 arenas (2-25), distribute quota evenly
            self.arena_quotas = {}
            quota_per_arena = total_quota // 24
            for arena in range(2, 26):  # Arenas 2-25
                self.arena_quotas[arena] = quota_per_arena
            print(f"🎯 Arena-based quotas: {quota_per_arena} players per arena")
            
        elif strategy == "bucket_based":
            # 100-trophy buckets from 0-10000
            self.bucket_quotas = {}
            buckets = list(range(0, 10000, 100))
            quota_per_bucket = total_quota // len(buckets)
            for i in range(len(buckets)):
                bucket_range = f"{buckets[i]}-{buckets[i]+99}"
                self.bucket_quotas[bucket_range] = quota_per_bucket
            print(f"🎯 Bucket-based quotas: {quota_per_bucket} players per 100-trophy bucket")
            
        elif strategy == "hybrid":
            # Combine arena and bucket for finer control
            self.hybrid_quotas = defaultdict(int)
            # You can customize this based on your needs
            print("🎯 Hybrid quota system activated")
        
        # Track current counts
        self.arena_counts = defaultdict(int)
        self.bucket_counts = defaultdict(int)
        self.total_collected = 0
        
    def get_player_arena(self, trophies: int) -> int:
        """Determine arena based on trophy count"""
        arena_ranges = {
            2: (0, 299), 3: (300, 599), 4: (600, 999), 5: (1000, 1299),
            6: (1300, 1599), 7: (1600, 1999), 8: (2000, 2299), 9: (2300, 2599),
            10: (2600, 2999), 11: (3000, 3399), 12: (3400, 3799), 13: (3800, 4199),
            14: (4200, 4599), 15: (4600, 4999), 16: (5000, 5499), 17: (5500, 5999),
            18: (6000, 6499), 19: (6500, 6999), 20: (7000, 7499), 21: (7500, 7999),
            22: (8000, 8499), 23: (8500, 8999), 24: (9000, 9499), 25: (9500, 10000)
        }
        
        for arena, (low, high) in arena_ranges.items():
            if low <= trophies <= high:
                return arena
        return 25  # Default to highest arena
    
    def get_player_bucket(self, trophies: int) -> str:
        """Get 100-trophy bucket for player"""
        bucket_start = (trophies // 100) * 100
        return f"{bucket_start}-{bucket_start+99}"
    
    def is_player_needed(self, player_trophies: int) -> bool:
        """Check if we need more players in this trophy range"""
        with self.quota_lock:
            if self.total_collected >= self.total_quota:
                return False
            
            if self.strategy == "arena_based":
                arena = self.get_player_arena(player_trophies)
                return self.arena_counts[arena] < self.arena_quotas.get(arena, 0)
                
            elif self.strategy == "bucket_based":
                bucket = self.get_player_bucket(player_trophies)
                return self.bucket_counts[bucket] < self.bucket_quotas.get(bucket, 0)
                
            elif self.strategy == "hybrid":
                # More sophisticated logic can be added here
                return self.total_collected < self.total_quota
                
            return True
    
    def register_player(self, player_trophies: int):
        """Register a new player in the quota system"""
        with self.quota_lock:
            self.total_collected += 1
            
            if self.strategy == "arena_based":
                arena = self.get_player_arena(player_trophies)
                self.arena_counts[arena] += 1
                
            elif self.strategy == "bucket_based":
                bucket = self.get_player_bucket(player_trophies)
                self.bucket_counts[bucket] += 1
    
    def get_quota_progress(self) -> Dict[str, Any]:
        """Get current progress towards quotas"""
        with self.quota_lock:
            progress = {
                'total_collected': self.total_collected,
                'total_quota': self.total_quota,
                'completion_percentage': (self.total_collected / self.total_quota) * 100
            }
            
            if self.strategy == "arena_based":
                progress['arena_progress'] = {
                    arena: {'current': self.arena_counts[arena], 'quota': self.arena_quotas[arena]}
                    for arena in sorted(self.arena_quotas.keys())
                }
                
            elif self.strategy == "bucket_based":
                progress['bucket_progress'] = {
                    bucket: {'current': self.bucket_counts[bucket], 'quota': self.bucket_quotas[bucket]}
                    for bucket in sorted(self.bucket_quotas.keys())
                }
            
            return progress
    
    def print_quota_progress(self):
        """Print current quota progress"""
        progress = self.get_quota_progress()
        
        print(f"\n📊 QUOTA PROGRESS: {progress['total_collected']:,}/{progress['total_quota']:,} "
              f"({progress['completion_percentage']:.1f}%)")
        
        if self.strategy == "arena_based" and 'arena_progress' in progress:
            print("🏆 Arena Distribution:")
            for arena, data in progress['arena_progress'].items():
                pct = (data['current'] / data['quota']) * 100 if data['quota'] > 0 else 0
                status = "✅" if pct >= 100 else "🟡" if pct >= 80 else "🔴"
                print(f"   Arena {arena:2d}: {data['current']:4d}/{data['quota']:4d} ({pct:5.1f}%) {status}")
                
        elif self.strategy == "bucket_based" and 'bucket_progress' in progress:
            print("📈 Bucket Distribution (showing incomplete):")
            incomplete_buckets = 0
            for bucket, data in progress['bucket_progress'].items():
                pct = (data['current'] / data['quota']) * 100 if data['quota'] > 0 else 0
                if pct < 100:
                    incomplete_buckets += 1
                    if incomplete_buckets <= 10:  # Show first 10 incomplete buckets
                        status = "🟡" if pct >= 80 else "🔴"
                        print(f"   {bucket:8} trophies: {data['current']:3d}/{data['quota']:3d} ({pct:5.1f}%) {status}")
            if incomplete_buckets > 10:
                print(f"   ... and {incomplete_buckets - 10} more incomplete buckets")
    
    def get_player_data(self, player_tag: str) -> Optional[Dict[str, Any]]:
        """Fetch player data including profile and battle logs"""
        try:
            url = f"{self.base_url}/profile/{player_tag}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching data for player {player_tag}: {e}")
            return None
    
    def get_current_player_trophies(self, player_data: Dict[str, Any]) -> int:
        """Extract current player's trophies from profile data"""
        return player_data.get('profile', {}).get('maxscore', 0)
    
    def extract_opponents_from_battle_log(self, player_data: Dict[str, Any], current_player_tag: str) -> List[Dict[str, Any]]:
        """Extract opponent information from player's battle logs"""
        opponents = []
        matches = player_data.get('matches', [])
        
        for match in matches:
            game_config = match.get('game_config', {})
            if game_config.get('name') != 'Ladder':
                continue
            
            players = match.get('players', [])
            if len(players) >= 2:
                opponent_data = players[1]
                opponent_trophies = opponent_data.get('score', 0)
                opponent_tag = opponent_data.get('hashtag', '')
                opponent_name = opponent_data.get('name', 'Unknown')
                
                if not opponent_tag or opponent_tag == current_player_tag:
                    continue
                
                # Only include opponents that we need (quota-based filtering)
                if self.is_player_needed(opponent_trophies):
                    opponent_info = {
                        'tag': opponent_tag,
                        'trophies': opponent_trophies,
                        'name': opponent_name,
                        'source_match_timestamp': match.get('timestamp'),
                        'game_mode': game_config.get('name', 'Ladder')
                    }
                    opponents.append(opponent_info)
        
        return opponents
    
    def process_single_player(self, player_data: Dict, width: int, delay: float, 
                            visited_players: Set, all_players: List, 
                            progress_counter: Dict) -> Tuple[List[Dict], int]:
        """Process a single player and return new opponents found"""
        current_player = player_data
        new_players = []
        new_count = 0
        
        time.sleep(delay)
        player_api_data = self.get_player_data(current_player['tag'])
        
        if not player_api_data or not player_api_data.get('success'):
            return new_players, new_count
        
        # Update current player's trophies if available
        current_trophies = self.get_current_player_trophies(player_api_data)
        if current_trophies > 0:
            with self.progress_lock:
                for player in all_players:
                    if player['tag'] == current_player['tag']:
                        player['trophies'] = current_trophies
                        break
        
        # Check if we've reached overall quota
        if self.total_collected >= self.total_quota:
            return new_players, new_count
        
        # Extract opponents (already filtered by quota system)
        all_opponents = self.extract_opponents_from_battle_log(player_api_data, current_player['tag'])
        
        # Select random opponents, but prioritize needed trophy ranges
        if len(all_opponents) > 0:
            # Simple random selection for now (can be enhanced with weighted selection)
            selected_opponents = random.sample(all_opponents, min(width, len(all_opponents)))
        else:
            selected_opponents = []
        
        # Process selected opponents
        for opponent in selected_opponents:
            opponent_tag = opponent['tag']
            
            with self.visited_lock:
                if opponent_tag not in visited_players and self.is_player_needed(opponent['trophies']):
                    visited_players.add(opponent_tag)
                    
                    new_player = {
                        'tag': opponent['tag'],
                        'trophies': opponent['trophies'],
                        'name': opponent['name'],
                        'source_player': current_player['tag'],
                        'depth': current_player.get('depth', 0) + 1,
                        'source_timestamp': opponent.get('source_match_timestamp'),
                        'game_mode': opponent.get('game_mode', 'Ladder')
                    }
                    
                    new_players.append(new_player)
                    new_count += 1
                    self.register_player(opponent['trophies'])
        
        # Update progress
        with self.progress_lock:
            progress_counter['processed'] += 1
            progress_counter['found_opponents'] += len(all_opponents)
            progress_counter['selected_opponents'] += len(selected_opponents)
            progress_counter['new_players'] += new_count
            
            # Print progress every 20 players or when quota progress updates
            if progress_counter['processed'] % 20 == 0 or progress_counter['processed'] == 1:
                elapsed = time.time() - progress_counter['start_time']
                rate = progress_counter['processed'] / elapsed if elapsed > 0 else 0
                remaining_players = self.total_quota - self.total_collected
                eta = remaining_players / rate if rate > 0 else 0
                
                print(f"   📊 Progress: {progress_counter['processed']} players processed | "
                      f"Total: {self.total_collected:,}/{self.total_quota:,} | "
                      f"Rate: {rate:.1f} players/s | ETA: {eta/60:.1f} min")
                
                # Show quota progress every 100 players
                if progress_counter['processed'] % 100 == 0:
                    self.print_quota_progress()
        
        return new_players, new_count
    
    def expand_player_network_uniform(self, initial_players: List[Dict], width: int = 3, 
                                    max_depth: int = 10, delay: float = 1.0) -> List[Dict]:
        """Expand player network with uniform distribution quotas"""
        visited_players = set()
        all_players = []
        queue = deque()
        
        # Add initial players to queue and register them
        for player in initial_players:
            player_tag = player['tag']
            if player_tag not in visited_players and self.is_player_needed(player['trophies']):
                visited_players.add(player_tag)
                player_with_depth = player.copy()
                player_with_depth['depth'] = 0
                player_with_depth['source'] = 'initial_dataset'
                all_players.append(player_with_depth)
                self.register_player(player['trophies'])
                queue.append(player_with_depth)
        
        print(f"🚀 Starting UNIFORM network expansion with {len(initial_players)} initial players")
        print(f"📊 Parameters: width={width}, max_depth={max_depth}, workers={self.max_workers}, delay={delay}s")
        print(f"🎯 Target: {self.total_quota:,} players with {self.strategy} distribution")
        
        start_time = time.time()
        current_depth = 0
        
        while queue and current_depth < max_depth and self.total_collected < self.total_quota:
            current_level_players = list(queue)
            queue.clear()
            
            if not current_level_players:
                break
            
            print(f"\n🎯 Processing depth {current_depth}: {len(current_level_players)} players")
            
            progress_counter = {
                'processed': 0,
                'total_players': len(current_level_players),
                'found_opponents': 0,
                'selected_opponents': 0,
                'new_players': 0,
                'start_time': time.time()
            }
            
            # Process players in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_player = {
                    executor.submit(
                        self.process_single_player, 
                        player, width, delay, visited_players, all_players, progress_counter
                    ): player for player in current_level_players
                }
                
                for future in as_completed(future_to_player):
                    if self.total_collected >= self.total_quota:
                        # Cancel remaining tasks if quota reached
                        for f in future_to_player:
                            f.cancel()
                        break
                        
                    player = future_to_player[future]
                    try:
                        new_players, new_count = future.result()
                        for new_player in new_players:
                            queue.append(new_player)
                            all_players.append(new_player)
                    except Exception as exc:
                        print(f"❌ Player {player['tag']} generated an exception: {exc}")
            
            current_depth += 1
            level_time = time.time() - progress_counter['start_time']
            print(f"   ✅ Depth {current_depth-1} completed in {level_time:.1f}s")
            print(f"   📈 Found {progress_counter['found_opponents']} needed opponents, "
                  f"added {progress_counter['new_players']} new players")
            
            # Check if we should continue
            if self.total_collected >= self.total_quota:
                print(f"   🎉 Quota reached! Stopping expansion.")
                break
        
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"📈 UNIFORM NETWORK EXPANSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total players collected: {len(all_players):,}")
        print(f"Unique players: {len(visited_players):,}")
        print(f"Target quota: {self.total_quota:,}")
        print(f"Quota completion: {self.total_collected:,}/{self.total_quota:,} ({self.total_collected/self.total_quota*100:.1f}%)")
        print(f"Maximum depth reached: {current_depth}")
        print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Processing rate: {len(all_players)/total_time:.2f} players/second")
        
        # Final quota progress
        self.print_quota_progress()
        
        return all_players
    
    def load_initial_players(self, filename: str = "clash_royale_arenas_complete.json") -> List[Dict[str, Any]]:
        """Load initial players from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                players_data = json.load(f)
            
            print(f"✅ Loaded {len(players_data)} initial players from {filename}")
            
            validated_players = []
            for player in players_data:
                if 'tag' in player and 'trophies' in player:
                    validated_player = {
                        'tag': player['tag'],
                        'trophies': player['trophies'],
                        'name': player.get('name', 'Unknown')
                    }
                    if 'arena' in player:
                        validated_player['arena'] = player['arena']
                    if 'target_arena' in player:
                        validated_player['target_arena'] = player['target_arena']
                    validated_players.append(validated_player)
            
            return validated_players
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return []
        except json.JSONDecodeError:
            print(f"❌ Error decoding JSON from {filename}")
            return []
    
    def save_expanded_data(self, players_data: List[Dict], filename: str = "clash_royale_uniform.json"):
        """Save expanded player data to JSON file"""
        metadata = {
            'total_players': len(players_data),
            'scraping_timestamp': time.time(),
            'description': f'Uniform player network - {self.strategy} distribution',
            'scraping_method': 'uniform_parallel_bfs',
            'total_quota': self.total_quota,
            'quota_strategy': self.strategy,
            'quota_achieved': self.total_collected
        }
        
        output_data = {
            'metadata': metadata,
            'players': players_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Uniform data saved to {filename}")
        print(f"📊 Total players: {len(players_data):,}")
    
    def run_uniform_expansion(self, input_file: str = "clash_royale_arenas_complete.json",
                            output_file: str = "clash_royale_uniform.json",
                            total_quota: int = 50000,
                            strategy: str = "arena_based",
                            width: int = 3, 
                            max_depth: int = 10, 
                            delay: float = 1.0):
        """Run the complete uniform expansion pipeline"""
        print("🎯 Starting UNIFORM Clash Royale Network Expansion")
        print(f"📁 Input: {input_file}")
        print(f"💾 Output: {output_file}")
        
        # Setup quota system
        self.setup_quota_system(total_quota, strategy)
        
        # Load initial players
        initial_players = self.load_initial_players(input_file)
        
        if not initial_players:
            print("❌ No initial players found. Please check the input file.")
            return
        
        # Expand network with uniform distribution
        expanded_players = self.expand_player_network_uniform(
            initial_players=initial_players,
            width=width,
            max_depth=max_depth,
            delay=delay
        )
        
        # Save results
        self.save_expanded_data(expanded_players, output_file)
        
        print(f"\n🎉 UNIFORM expansion completed successfully!")
        print(f"📈 Network grew from {len(initial_players)} to {len(expanded_players):,} players")
        print(f"📊 Quota achievement: {self.total_collected:,}/{total_quota:,} ({self.total_collected/total_quota*100:.1f}%)")

def visualize_uniform_data(data_file: str = "clash_royale_uniform.json"):
    """Visualize the uniform player data"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'players' in data:
            players_data = data['players']
            metadata = data.get('metadata', {})
        else:
            players_data = data
            metadata = {}
        
        print(f"📊 Visualizing uniform data: {len(players_data):,} players")
        if metadata:
            print(f"📋 Metadata: {metadata}")
        
        from trophy_vis import TrophyDistributionVisualizer
        visualizer = TrophyDistributionVisualizer()
        visualizer.create_comprehensive_visualizations(players_data, "uniform_visualizations")
        
    except FileNotFoundError:
        print(f"❌ File {data_file} not found")
    except Exception as e:
        print(f"❌ Error visualizing uniform data: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Expand Clash Royale player network with uniform distribution')
    parser.add_argument('--input', default='clash_royale_arenas_complete.json', 
                       help='Input JSON file with initial players')
    parser.add_argument('--output', default='clash_royale_uniform.json', 
                       help='Output JSON file for expanded data')
    parser.add_argument('--quota', type=int, default=50000, 
                       help='Total number of players to collect')
    parser.add_argument('--strategy', choices=['arena_based', 'bucket_based', 'hybrid'], 
                       default='arena_based', help='Quota distribution strategy')
    parser.add_argument('--width', type=int, default=3, 
                       help='Number of random opponents to select per player')
    parser.add_argument('--max-depth', type=int, default=10, 
                       help='Maximum expansion depth')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between API calls in seconds')
    parser.add_argument('--workers', type=int, default=5, 
                       help='Number of parallel workers')
    parser.add_argument('--visualize', action='store_true', 
                       help='Run visualization after expansion')
    
    args = parser.parse_args()
    
    # Run uniform expansion
    scraper = UniformClashRoyaleScraper(max_workers=args.workers)
    scraper.run_uniform_expansion(
        input_file=args.input,
        output_file=args.output,
        total_quota=args.quota,
        strategy=args.strategy,
        width=args.width,
        max_depth=args.max_depth,
        delay=args.delay
    )
    
    # Run visualization if requested
    if args.visualize:
        print(f"\n📊 Generating visualizations...")
        visualize_uniform_data(args.output)

if __name__ == "__main__":
    main()