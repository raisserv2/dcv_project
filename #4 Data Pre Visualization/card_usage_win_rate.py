import csv
from collections import defaultdict
import ast

# Initialize counters
card_usage_counter = defaultdict(int)
card_win_counter = defaultdict(int)

# Read the CSV file
with open('../Processed Data/preprocessed_battle_log.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        # Process player 0's deck
        player0_spells = row['players_0_spells']
        player0_winner = int(row['players_0_winner'])
        
        # Process player 1's deck  
        player1_spells = row['players_1_spells']
        player1_winner = int(row['players_1_winner'])
        
        # Parse the spells strings into actual lists
        try:
            player0_cards_list = ast.literal_eval(player0_spells)
            player1_cards_list = ast.literal_eval(player1_spells)
        except:
            print(f"Error parsing spells for row: {row.get('replayTag', 'Unknown')}")
            continue
        
        # For card usage counter (unique decks per player)
        player0_cards = set()
        player1_cards = set()
        
        # Extract card names from player 0
        for card_tuple in player0_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                card_name = card_tuple[0]
                player0_cards.add(card_name)
        
        # Extract card names from player 1
        for card_tuple in player1_cards_list:
            if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                card_name = card_tuple[0]
                player1_cards.add(card_name)
        
        # Add to usage counter (only count each card once per player)
        for card in player0_cards:
            card_usage_counter[card] += 1
        
        for card in player1_cards:
            card_usage_counter[card] += 1
        
        # For win percentage counter (count all cards in winning decks)
        if player0_winner == 1:  # Player 0 won
            for card_tuple in player0_cards_list:
                if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                    card_name = card_tuple[0]
                    card_win_counter[card_name] += 1
        
        if player1_winner == 1:  # Player 1 won
            for card_tuple in player1_cards_list:
                if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                    card_name = card_tuple[0]
                    card_win_counter[card_name] += 1

# Convert to regular dictionaries for easier handling
card_usage_dict = dict(card_usage_counter)
card_win_dict = dict(card_win_counter)

print("Card Usage Counter (for pie chart):")
print(card_usage_dict)
print(f"\nTotal unique cards: {len(card_usage_dict)}")
print(f"Total card appearances: {sum(card_usage_dict.values())}")

print("\n" + "="*50 + "\n")

print("Card Win Counter (for win percentage):")
print(card_win_dict)
print(f"\nTotal unique cards in winning decks: {len(card_win_dict)}")
print(f"Total card appearances in winning decks: {sum(card_win_dict.values())}")

# Optional: Show top 10 most used cards
print("\n" + "="*50)
print("Top 10 Most Used Cards:")
sorted_usage = sorted(card_usage_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, count) in enumerate(sorted_usage[:10], 1):
    print(f"{i}. {card}: {count}")

print("\nTop 10 Most Winning Cards:")
sorted_wins = sorted(card_win_dict.items(), key=lambda x: x[1], reverse=True)
for i, (card, count) in enumerate(sorted_wins[:10], 1):
    print(f"{i}. {card}: {count}")