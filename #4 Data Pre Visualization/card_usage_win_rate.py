import csv
from collections import defaultdict
import ast

# Initialize counters
card_usage_counter = defaultdict(int)  # Unique player-deck combinations
card_win_counter = defaultdict(int)    # Cards in winning decks
card_total_plays_counter = defaultdict(int)  # Total times card was played (for win percentage)

# Track unique player-deck combinations to avoid duplicates for usage counter
player_deck_combinations = set()

# Read the CSV file
with open('../#2 Data Storage/Processed Data/preprocessed_battle_log.csv', 'r', encoding='utf-8') as file:
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
        
        # Extract unique cards from both players' decks
        player0_unique_cards = set()
        for card_tuple in player0_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                card_name = card_tuple[0]
                player0_unique_cards.add(card_name)
        
        player1_unique_cards = set()
        for card_tuple in player1_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                card_name = card_tuple[0]
                player1_unique_cards.add(card_name)
        
        # Process player 0 for USAGE counter - only count if we haven't seen this player with this deck before
        if player0_deck_id not in player_deck_combinations:
            player_deck_combinations.add(player0_deck_id)
            
            # Add to usage counter
            for card in player0_unique_cards:
                card_usage_counter[card] += 1
        
        # Process player 1 for USAGE counter - only count if we haven't seen this player with this deck before
        if player1_deck_id not in player_deck_combinations:
            player_deck_combinations.add(player1_deck_id)
            
            # Add to usage counter
            for card in player1_unique_cards:
                card_usage_counter[card] += 1
        
        # Process player 0 for TOTAL PLAYS counter and WIN counter
        for card in player0_unique_cards:
            card_total_plays_counter[card] += 1
            
            if player0_winner == 1:  # Player 0 won
                card_win_counter[card] += 1
        
        # Process player 1 for TOTAL PLAYS counter and WIN counter
        for card in player1_unique_cards:
            card_total_plays_counter[card] += 1
            
            if player1_winner == 1:  # Player 1 won
                card_win_counter[card] += 1

# Convert to regular dictionaries for easier handling
card_usage_dict = dict(card_usage_counter)
card_win_dict = dict(card_win_counter)
card_total_plays_dict = dict(card_total_plays_counter)

# Calculate win percentages
card_win_percentage_dict = {}
for card in card_total_plays_dict:
    if card_total_plays_dict[card] > 0:
        win_percentage = (card_win_dict.get(card, 0) / card_total_plays_dict[card]) * 100
        card_win_percentage_dict[card] = round(win_percentage, 2)

print("Card Usage Counter (for pie chart - unique player-deck combinations):")
print(card_usage_dict)
print(f"\nTotal unique cards: {len(card_usage_dict)}")
print(f"Total card appearances in unique decks: {sum(card_usage_dict.values())}")
print(f"Unique player-deck combinations: {len(player_deck_combinations)}")

print("\n" + "="*50 + "\n")

print("Card Total Plays Counter (for win percentage denominator):")
print(card_total_plays_dict)
print(f"\nTotal unique cards played: {len(card_total_plays_dict)}")
print(f"Total card plays: {sum(card_total_plays_dict.values())}")

print("\n" + "="*50 + "\n")

print("Card Win Counter (for win percentage numerator):")
print(card_win_dict)
print(f"\nTotal unique cards in winning decks: {len(card_win_dict)}")
print(f"Total winning card appearances: {sum(card_win_dict.values())}")

print("\n" + "="*50 + "\n")

print("Card Win Percentage:")
print(card_win_percentage_dict)

# Optional: Show top cards with statistics
print("\n" + "="*50)
print("Top 15 Most Used Cards (Unique per Player-Deck):")
sorted_usage = sorted(card_usage_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, count) in enumerate(sorted_usage[:15], 1):
    print(f"{i}. {card}: {count}")

print("\nTop 15 Highest Win Rate Cards (min 5 plays):")
# Filter cards with minimum plays for meaningful statistics
filtered_win_rates = {card: rate for card, rate in card_win_percentage_dict.items() 
                     if card_total_plays_dict.get(card, 0) >= 5}
sorted_win_rates = sorted(filtered_win_rates.items(), key=lambda x: x[1], reverse=True)
for i, (card, rate) in enumerate(sorted_win_rates[:15], 1):
    plays = card_total_plays_dict.get(card, 0)
    wins = card_win_dict.get(card, 0)
    print(f"{i}. {card}: {rate}% ({wins}/{plays})")

print("\nTop 15 Most Winning Cards (by raw wins):")
sorted_wins = sorted(card_win_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, wins) in enumerate(sorted_wins[:15], 1):
    plays = card_total_plays_dict.get(card, 0)
    rate = card_win_percentage_dict.get(card, 0)
    print(f"{i}. {card}: {wins} wins ({rate}% from {plays} plays)")