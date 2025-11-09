import pandas as pd
import ast
import json
import functools
from collections import defaultdict
import concurrent.futures

# --- 1. ARENA MAPPING ---
ARENA_ID_TO_NUMBER_MAP = {
    '54000002': '2', '54000003': '3', '54000004': '4', '54000005': '5',
    '54000006': '6', '54000008': '7', '54000009': '8', '54000010': '9',
    '54000007': '10', '54000024': '11', '54000011': '12', '54000055': '13',
    '54000056': '14', '54000012': '15', '54000013': '16', '54000014': '17',
    '54000015': '18', '54000016': '19', '54000017': '20', '54000018': '21',
    '54000019': '22', '54000020': '23', '54000031': '24', '54000117': '25'
}

# --- 2. HELPER FUNCTIONS ---

def convert_data(path):
    data = pd.read_csv(path)
    data['arena'] = data['arena'].astype(str)
    data['arena_num'] = data['arena'].map(ARENA_ID_TO_NUMBER_MAP)
    
    player_tag = pd.concat([data['players_0_hashtag'], data['players_1_hashtag']], ignore_index=True)
    spells = pd.concat([data['players_0_spells'], data['players_1_spells']], ignore_index=True)
    arena = pd.concat([data['arena_num'], data['arena_num']], ignore_index=True)
    
    new_data = pd.DataFrame({
        'player_tag': player_tag,
        'card_list': spells,
        'arena': arena
    })
    
    new_data = new_data.dropna(subset=['arena'])
    data = new_data.drop_duplicates(subset='player_tag', keep='first')
    return data

def process_dataframe_with_totals(input_df):
    ARENA_COLUMN_NAME = 'arena'
    CARDS_COLUMN_NAME = 'card_list'
    arena_card_counts = defaultdict(lambda: defaultdict(int))
    
    for _, row in input_df.iterrows():
        try:
            arena_num = row[ARENA_COLUMN_NAME]
            card_list_str = row[CARDS_COLUMN_NAME]
            
            # --- Use the correct parser for [('Card', 11, 0), ...] ---
            card_list = ast.literal_eval(card_list_str)
            if not isinstance(card_list, list):
                continue
                
            for card_tuple in card_list:
                if isinstance(card_tuple, tuple) and len(card_tuple) > 0:
                    arena_card_counts[arena_num][card_tuple[0]] += 1
            # --------------------------------------------------------
                    
        except (ValueError, SyntaxError, TypeError, KeyError):
            pass 

    final_dict = {}
    for arena, counts in arena_card_counts.items():
        total_count = sum(counts.values())
        final_arena_data = dict(counts)
        final_arena_data['total_cards'] = total_count
        final_dict[arena] = final_arena_data
    return final_dict

def add_arena_dicts(dict1, dict2):
    merged_counts = defaultdict(lambda: defaultdict(int))
    def populate_counts(source_dict):
        for arena, inner_dict in source_dict.items():
            for card, count in inner_dict.items():
                if card != 'total_cards':
                    merged_counts[arena][card] += count
    populate_counts(dict1)
    populate_counts(dict2)
    final_dict = {}
    for arena, counts in merged_counts.items():
        total = sum(counts.values())
        final_arena_data = dict(counts)
        final_arena_data['total_cards'] = total
        final_dict[arena] = final_arena_data
    return final_dict

def calculate_card_percentages(arena_counts):
    all_arenas = list(arena_counts.keys())
    all_cards = set()
    for inner_dict in arena_counts.values():
        for card in inner_dict.keys():
            if card != 'total_cards':
                all_cards.add(card)
                
    card_percentages = {}
    for card in all_cards:
        card_percentages[card] = {arena: 0.0 for arena in all_arenas}
            
    for arena, inner_dict in arena_counts.items():
        total = inner_dict.get('total_cards', 0)
        if total == 0:
            continue
        for card, count in inner_dict.items():
            if card == 'total_cards':
                continue
            percentage = (count / total) * 100.0
            card_percentages[card][arena] = round(percentage, 2)
    return card_percentages

def process_item_to_dict(item):
    try:
        dataframe = convert_data(item) 
        arena_dict = process_dataframe_with_totals(dataframe)
        return arena_dict
    except Exception as e:
        print(f"Error processing item {item}: {e}")
        return None

# --- 3. MAIN EXECUTION (PROCESS & SAVE) ---
def main_process_and_save():
    input_data = ["/Users/raghava/Downloads/New Folder With Items/preprocessed_battle_log_full_batch-2.csv"]
    output_filename = "/Users/raghava/Downloads/card_percentage_dict.json"

    print(f"Starting parallel processing for {len(input_data)} items...")
    converted_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results_iterator = executor.map(process_item_to_dict, input_data)
        converted_data = [result for result in results_iterator if result is not None]
    
    print(f"Successfully processed {len(converted_data)} items.")

    if not converted_data:
        print("No data processed. Exiting.")
        return
        
    print("Merging processed data...")
    arens_dict = functools.reduce(add_arena_dicts, converted_data)

    print("Calculating percentages...")
    card_percentage_dict = calculate_card_percentages(arens_dict)

    # --- NEW: SAVE THE DICTIONARY TO A JSON FILE ---
    print(f"Saving data to {output_filename}...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            # json.dump writes the dictionary to the file
            # indent=2 makes it human-readable
            json.dump(card_percentage_dict, f, indent=2)
        print(f"\n--- SUCCESS ---")
        print(f"Card percentage dictionary saved to: {output_filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

if __name__ == "__main__":
    main_process_and_save()