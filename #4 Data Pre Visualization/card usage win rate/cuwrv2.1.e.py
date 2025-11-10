import csv
from collections import defaultdict
import ast
import json
import pandas as pd
import pickle

# Initialize counters for EVO and NON-EVO cards
evo_card_usage_counter = defaultdict(int)
evo_card_win_counter = defaultdict(int)
evo_card_total_plays_counter = defaultdict(int)

non_evo_card_usage_counter = defaultdict(int)
non_evo_card_win_counter = defaultdict(int)
non_evo_card_total_plays_counter = defaultdict(int)

# Track unique player-deck combinations to avoid duplicates for usage counter
player_deck_combinations = set()

print("Processing Clash Royale battle data (separating EVO vs NON-EVO)...")

# Read the CSV file
with open('../../#2 Data Storage/Processed Data/fullbatch.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        # Get player identifiers and winner status
        player0_hashtag = row['players_0_hashtag']
        player1_hashtag = row['players_1_hashtag']
        player0_winner = int(row['players_0_winner'])
        player1_winner = int(row['players_1_winner'])
        
        # Process player 0's deck
        player0_spells = row['players_0_spells']
        
        # Process player 1's deck  
        player1_spells = row['players_1_spells']
        
        # Parse the spells strings into actual lists
        try:
            player0_cards_list = ast.literal_eval(player0_spells)
            player1_cards_list = ast.literal_eval(player1_spells)
        except:
            print(f"Error parsing spells for row: {row.get('replayTag', 'Unknown')}")
            continue
        
        # Create unique identifiers for player-deck combinations
        player0_deck_id = (player0_hashtag, tuple(sorted([card[0] for card in player0_cards_list if isinstance(card, tuple) and len(card) > 0])))
        player1_deck_id = (player1_hashtag, tuple(sorted([card[0] for card in player1_cards_list if isinstance(card, tuple) and len(card) > 0])))
        
        # Extract cards from both players' decks, separating EVO and NON-EVO
        player0_evo_cards = set()
        player0_non_evo_cards = set()
        for card_tuple in player0_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) >= 3:
                card_name = card_tuple[0]
                is_evo = card_tuple[2]  # 3rd element indicates evolution (1 = EVO, 0 = NON-EVO)
                if is_evo == 1:
                    player0_evo_cards.add(card_name)
                else:
                    player0_non_evo_cards.add(card_name)
        
        player1_evo_cards = set()
        player1_non_evo_cards = set()
        for card_tuple in player1_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) >= 3:
                card_name = card_tuple[0]
                is_evo = card_tuple[2]  # 3rd element indicates evolution (1 = EVO, 0 = NON-EVO)
                if is_evo == 1:
                    player1_evo_cards.add(card_name)
                else:
                    player1_non_evo_cards.add(card_name)
        
        # Process player 0 for USAGE counter - only count if we haven't seen this player with this deck before
        if player0_deck_id not in player_deck_combinations:
            player_deck_combinations.add(player0_deck_id)
            
            # Add to EVO usage counter
            for card in player0_evo_cards:
                evo_card_usage_counter[card] += 1
            
            # Add to NON-EVO usage counter
            for card in player0_non_evo_cards:
                non_evo_card_usage_counter[card] += 1
        
        # Process player 1 for USAGE counter - only count if we haven't seen this player with this deck before
        if player1_deck_id not in player_deck_combinations:
            player_deck_combinations.add(player1_deck_id)
            
            # Add to EVO usage counter
            for card in player1_evo_cards:
                evo_card_usage_counter[card] += 1
            
            # Add to NON-EVO usage counter
            for card in player1_non_evo_cards:
                non_evo_card_usage_counter[card] += 1
        
        # Process player 0 for TOTAL PLAYS counter and WIN counter
        for card in player0_evo_cards:
            evo_card_total_plays_counter[card] += 1
            if player0_winner == 1:  # Player 0 won
                evo_card_win_counter[card] += 1
        
        for card in player0_non_evo_cards:
            non_evo_card_total_plays_counter[card] += 1
            if player0_winner == 1:  # Player 0 won
                non_evo_card_win_counter[card] += 1
        
        # Process player 1 for TOTAL PLAYS counter and WIN counter
        for card in player1_evo_cards:
            evo_card_total_plays_counter[card] += 1
            if player1_winner == 1:  # Player 1 won
                evo_card_win_counter[card] += 1
        
        for card in player1_non_evo_cards:
            non_evo_card_total_plays_counter[card] += 1
            if player1_winner == 1:  # Player 1 won
                non_evo_card_win_counter[card] += 1

# Convert to regular dictionaries for easier handling
evo_card_usage_dict = dict(evo_card_usage_counter)
evo_card_win_dict = dict(evo_card_win_counter)
evo_card_total_plays_dict = dict(evo_card_total_plays_counter)

non_evo_card_usage_dict = dict(non_evo_card_usage_counter)
non_evo_card_win_dict = dict(non_evo_card_win_counter)
non_evo_card_total_plays_dict = dict(non_evo_card_total_plays_counter)

# Calculate win percentages for EVO cards
evo_card_win_percentage_dict = {}
for card in evo_card_total_plays_dict:
    if evo_card_total_plays_dict[card] > 0:
        win_percentage = (evo_card_win_dict.get(card, 0) / evo_card_total_plays_dict[card]) * 100
        evo_card_win_percentage_dict[card] = round(win_percentage, 2)

# Calculate win percentages for NON-EVO cards
non_evo_card_win_percentage_dict = {}
for card in non_evo_card_total_plays_dict:
    if non_evo_card_total_plays_dict[card] > 0:
        win_percentage = (non_evo_card_win_dict.get(card, 0) / non_evo_card_total_plays_dict[card]) * 100
        non_evo_card_win_percentage_dict[card] = round(win_percentage, 2)

print("Processing complete! Saving data to files...")

# Create comprehensive DataFrames for visualization
# EVO Cards DataFrame
evo_card_data = []
for card in set(evo_card_usage_dict.keys()) | set(evo_card_win_percentage_dict.keys()):
    evo_card_data.append({
        'card': card,
        'usage_count': evo_card_usage_dict.get(card, 0),
        'win_count': evo_card_win_dict.get(card, 0),
        'total_plays': evo_card_total_plays_dict.get(card, 0),
        'win_percentage': evo_card_win_percentage_dict.get(card, 0),
        'card_type': 'EVO'
    })

evo_df = pd.DataFrame(evo_card_data)
evo_df.to_csv('clash_royale_card_stats_evo.csv', index=False)
evo_df.to_pickle('clash_royale_card_stats_evo.pkl')

# NON-EVO Cards DataFrame
non_evo_card_data = []
for card in set(non_evo_card_usage_dict.keys()) | set(non_evo_card_win_percentage_dict.keys()):
    non_evo_card_data.append({
        'card': card,
        'usage_count': non_evo_card_usage_dict.get(card, 0),
        'win_count': non_evo_card_win_dict.get(card, 0),
        'total_plays': non_evo_card_total_plays_dict.get(card, 0),
        'win_percentage': non_evo_card_win_percentage_dict.get(card, 0),
        'card_type': 'NON_EVO'
    })

non_evo_df = pd.DataFrame(non_evo_card_data)
non_evo_df.to_csv('clash_royale_card_stats_non_evo.csv', index=False)
non_evo_df.to_pickle('clash_royale_card_stats_non_evo.pkl')

# Save combined data as pickle for easy access
with open('clash_royale_data_separated.pkl', 'wb') as f:
    pickle.dump({
        'evo': {
            'usage': evo_card_usage_dict,
            'wins': evo_card_win_dict,
            'total_plays': evo_card_total_plays_dict,
            'win_percentage': evo_card_win_percentage_dict
        },
        'non_evo': {
            'usage': non_evo_card_usage_dict,
            'wins': non_evo_card_win_dict,
            'total_plays': non_evo_card_total_plays_dict,
            'win_percentage': non_evo_card_win_percentage_dict
        },
        'unique_decks': len(player_deck_combinations)
    }, f)

# Print summary statistics
print("\n" + "="*60)
print("DATA PROCESSING SUMMARY - EVO vs NON-EVO CARDS")
print("="*60)
print(f"Total unique player-deck combinations: {len(player_deck_combinations)}")

print("\nEVO CARDS:")
print(f"  Unique EVO cards: {len(evo_card_usage_dict)}")
print(f"  EVO card appearances in unique decks: {sum(evo_card_usage_dict.values())}")
print(f"  Total EVO card plays: {sum(evo_card_total_plays_dict.values())}")
print(f"  Total EVO winning card appearances: {sum(evo_card_win_dict.values())}")

print("\nNON-EVO CARDS:")
print(f"  Unique NON-EVO cards: {len(non_evo_card_usage_dict)}")
print(f"  NON-EVO card appearances in unique decks: {sum(non_evo_card_usage_dict.values())}")
print(f"  Total NON-EVO card plays: {sum(non_evo_card_total_plays_dict.values())}")
print(f"  Total NON-EVO winning card appearances: {sum(non_evo_card_win_dict.values())}")

print("\n" + "="*60)
print("TOP EVO CARDS SUMMARY")
print("="*60)

print("\nTop 10 Most Used EVO Cards:")
sorted_evo_usage = sorted(evo_card_usage_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, count) in enumerate(sorted_evo_usage[:10], 1):
    win_rate = evo_card_win_percentage_dict.get(card, 0)
    print(f"{i}. {card}: {count} decks, {win_rate}% win rate")

print("\nTop 10 Highest Win Rate EVO Cards (min 50 plays):")
filtered_evo_win_rates = {card: rate for card, rate in evo_card_win_percentage_dict.items() 
                         if evo_card_total_plays_dict.get(card, 0) >= 50}
sorted_evo_win_rates = sorted(filtered_evo_win_rates.items(), key=lambda x: x[1], reverse=True)
for i, (card, rate) in enumerate(sorted_evo_win_rates[:10], 1):
    plays = evo_card_total_plays_dict.get(card, 0)
    wins = evo_card_win_dict.get(card, 0)
    print(f"{i}. {card}: {rate}% ({wins}/{plays} plays)")

print("\n" + "="*60)
print("TOP NON-EVO CARDS SUMMARY")
print("="*60)

print("\nTop 10 Most Used NON-EVO Cards:")
sorted_non_evo_usage = sorted(non_evo_card_usage_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, count) in enumerate(sorted_non_evo_usage[:10], 1):
    win_rate = non_evo_card_win_percentage_dict.get(card, 0)
    print(f"{i}. {card}: {count} decks, {win_rate}% win rate")

print("\nTop 10 Highest Win Rate NON-EVO Cards (min 100 plays):")
filtered_non_evo_win_rates = {card: rate for card, rate in non_evo_card_win_percentage_dict.items() 
                             if non_evo_card_total_plays_dict.get(card, 0) >= 100}
sorted_non_evo_win_rates = sorted(filtered_non_evo_win_rates.items(), key=lambda x: x[1], reverse=True)
for i, (card, rate) in enumerate(sorted_non_evo_win_rates[:10], 1):
    plays = non_evo_card_total_plays_dict.get(card, 0)
    wins = non_evo_card_win_dict.get(card, 0)
    print(f"{i}. {card}: {rate}% ({wins}/{plays} plays)")

print("\n" + "="*60)
print("FILES SAVED:")
print("="*60)
print("1. clash_royale_card_stats_evo.csv - EVO cards DataFrame")
print("2. clash_royale_card_stats_evo.pkl - EVO cards DataFrame (pickle)")
print("3. clash_royale_card_stats_non_evo.csv - NON-EVO cards DataFrame")
print("4. clash_royale_card_stats_non_evo.pkl - NON-EVO cards DataFrame (pickle)")
print("5. clash_royale_data_separated.pkl - All separated data as Python object")

print("\nData is now ready for visualization!")