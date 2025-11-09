import pandas as pd
import itertools
import ast
import csv
from collections import defaultdict
def parse_deck_to_set(deck_str):
    """
    Safely parses a deck string like "[('Card1', 11, 0), ...]"
    into a set of card names {'Card1', ...}.
    """
    if pd.isna(deck_str) or not isinstance(deck_str, str):
        return set()
    if deck_str.strip() == "":
        return set()
            
    try:
        deck_list = ast.literal_eval(deck_str)
        
        if not isinstance(deck_list, list):
            return set()
        card_names = set()
        for card_tuple in deck_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                card_names.add(card_tuple[0])
        return card_names
    except (ValueError, SyntaxError, TypeError):
        return set()
def load_and_process_battles(csv_path, deck_col_0, deck_col_1, win_col_0, win_col_1):
    """
    Reads the raw battle log CSV and returns a list of all
    decks played, along with their win/loss status.
    """
    print(f"Loading raw battle data from: {csv_path}...")
    
    battles_data = []
    
    try:
        data = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
        
    for _, row in data.iterrows():
        try:
            # Get win/loss status
            player_0_status = float(row[win_col_0])
            player_1_status = float(row[win_col_1])

            # Skip draws
            if player_0_status == player_1_status:
                continue 
            
            player_0_won = player_0_status == 1
            player_1_won = player_1_status == 1
            
            # Get the decks for both players
            deck0_set = parse_deck_to_set(row[deck_col_0])
            deck1_set = parse_deck_to_set(row[deck_col_1])

            # Add both players' data to our list
            if deck0_set: # Only add if the deck isn't empty
                battles_data.append((deck0_set, player_0_won))
            if deck1_set:
                battles_data.append((deck1_set, player_1_won))
                
        except (TypeError, ValueError, KeyError) as e:
            # Skip rows with missing data
            print(f"Warning: Skipping a row due to bad data. Error: {e}")
            
    print(f"Successfully processed {len(battles_data)} individual decks.")
    return battles_data
def calculate_and_save_pair_stats(battles_data, all_cards_list, output_csv_path):
    """
    Calculates usage and win rate for all possible two-card pairs
    and saves the result to a CSV.
    """
    if not battles_data:
        print("Error: No battle data to process.")
        return

    print("Generating all possible card pairs...")
    sorted_cards = sorted(list(set(all_cards_list)))
    all_pairs_list = list(itertools.combinations(sorted_cards, 2))
    pair_stats = {pair: {'usage': 0, 'wins': 0} for pair in all_pairs_list}
    print(f"Analyzing {len(battles_data)} decks for {len(pair_stats)} pairs...")
    for (deck_set, won) in battles_data:
        deck_list_sorted = sorted(list(deck_set))
        for pair in itertools.combinations(deck_list_sorted, 2):
            if pair in pair_stats:
                pair_stats[pair]['usage'] += 1
                if won:
                    pair_stats[pair]['wins'] += 1
    print("Calculations complete. Preparing final CSV...")
    final_stats_list = []
    for pair, stats in pair_stats.items():
        usage = stats['usage']
        wins = stats['wins']
        win_rate = (wins / usage) * 100.0 if usage > 0 else 0.0    
        final_stats_list.append({
            'card_1': pair[0],
            'card_2': pair[1],
            'usage_count': usage,
            'win_rate_percent': round(win_rate, 2)
        })

    # 5. Save the results to the output CSV
    if not final_stats_list:
        print("Warning: No stats were generated.")
        return

    try:
        stats_df = pd.DataFrame(final_stats_list)
        
        # Sort by usage to see most popular pairs first
        stats_df = stats_df.sort_values(by='usage_count', ascending=False)
        
        stats_df.to_csv(output_csv_path, index=False)
        print(f"\n--- SUCCESS ---")
        print(f"Saved pair stats to: {output_csv_path}")
        print(stats_df.head())
        
    except Exception as e:
        print(f"Error saving file: {e}")
def main():
    ALL_CARDS_LIST = ['Mega Minion', 'Barbarians', 'Giant', 'Goblin Hut', 'Spear Goblins', 'Valkyrie', 'Knight', 'Mini P.E.K.K.A', 'Cannon', 'Tombstone', 'Bomber', 'Skeleton Army', 'Musketeer', 'Battle Ram', 'Fireball', 'Goblin Cage', 'Wizard', 'Minions', 'Witch', 'Skeleton Dragons', 'Mortar', 'Bats', 'Archers', 'Arrows', 'Skeletons', 'Royal Ghost', 'Hog Rider', 'Rocket', 'Zap', 'Flying Machine', 'Goblins', 'Inferno Tower', 'Bomb Tower', 'Fire Spirit', 'Electro Spirit', 'Baby Dragon', 'Goblin Barrel', 'Three Musketeers', 'P.E.K.K.A', 'Goblin Gang', 'Dart Goblin', 'Electro Dragon', 'Balloon', 'Vines', 'Prince', 'Mirror', 'Royal Hogs', 'Mega Knight', 'Sparky', 'Clone', 'X-Bow', 'Goblin Curse', 'Miner', 'Inferno Dragon', 'Suspicious Bush', 'Elixir Golem', 'Princess', 'The Log', 'Ice Wizard', 'Royal Recruits', 'Skeleton Barrel', 'Giant Skeleton', 'Skeleton King', 'Void', 'Night Witch', 'Lumberjack', 'Royal Giant', 'Lightning', 'Fisherman', 'Giant Snowball', 'Ice Spirit', 'Guards', 'Minion Horde', 'Electro Giant', 'Hunter', 'Zappies', 'Dark Prince', 'Barbarian Barrel', 'Tesla', 'Lava Hound', 'Tornado', 'Poison', 'Freeze', 'Executioner', 'Royal Delivery', 'Phoenix', 'Mother Witch', 'Bowler', 'Ram Rider', 'Firecracker', 'Graveyard', 'Battle Healer', 'Bandit', 'Rage', 'Elite Barbarians', 'Magic Archer', 'Rune Giant', 'Berserker', 'Rascals', 'Goblin Demolisher', 'Goblin Giant', 'Electro Wizard', 'Golem', 'Ice Golem', 'Wall Breakers', 'Goblin Machine', 'Furnace', 'Cannon Cart', 'Earthquake', 'Archer Queen', 'Golden Knight', 'Barbarian Hut', 'Goblin Drill', 'Heal Spirit', 'Mighty Miner', 'Little Prince', 'Elixir Collector', 'Boss Bandit', 'Goblinstein', 'Monk', 'Spirit Empress']
    
    INPUT_CSV_PATH = "preprocessed_battle_log_full_batch-2.csv"
    OUTPUT_CSV_PATH = "card_pair_data.csv"

    # --- 2. CONFIGURE YOUR COLUMN NAMES HERE ---
    
    DECK_COL_0 = 'players_0_spells'
    DECK_COL_1 = 'players_1_spells'
    
    WIN_COL_0 = 'players_0_winner'
    WIN_COL_1 = 'players_1_winner'

    # --- 3. RUN THE ANALYSIS ---
    
    # Step 1: Load and parse all battle data
    battles_data = load_and_process_battles(
        INPUT_CSV_PATH, 
        DECK_COL_0, 
        DECK_COL_1, 
        WIN_COL_0,
        WIN_COL_1
    )
    
    # Step 2: Calculate stats and save the CSV
    calculate_and_save_pair_stats(
        battles_data, 
        ALL_CARDS_LIST, 
        OUTPUT_CSV_PATH
    )

if __name__ == "__main__":
    main()