import pandas as pd
import ast
import warnings

# --- Setup ---
# Suppress warnings for cleaner output
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)

# Specify the input and output filenames
input_filename = "battle_log_data.csv"
output_filename = "preprocessed_battle_log.csv"

# --- Function to Parse Spells ---
def parse_spells(spells_str):
    """
    Safely evaluates a string representation of a list of dictionaries
    and converts it into a list of (icon, l) tuples.
    """
    # Handle empty or NaN values first
    if pd.isna(spells_str):
        return []  # Return an empty list for missing data
    
    try:
        # Safely evaluate the string as a Python literal (list of dicts)
        spells_list = ast.literal_eval(spells_str)
        
        # Ensure it's a list
        if not isinstance(spells_list, list):
            return []

        parsed_tuples = []
        for spell_dict in spells_list:
            # Ensure each item is a dict and has the required keys
            if isinstance(spell_dict, dict) and 'icon' in spell_dict and 'l' in spell_dict:
                parsed_tuples.append((spell_dict['icon'], spell_dict['l']))
        
        return parsed_tuples
    except (ValueError, SyntaxError, TypeError):
        # Handle cases where the string is not a valid list literal
        return []
    
# --- Parsing Function 2: Support Cards (NEW) ---
def parse_support_cards(support_cards_str):
    """
    Safely evaluates a string representation of a list of dictionaries
    and converts it into a list of (name, level) tuples.
    """
    if pd.isna(support_cards_str):
        return []
    try:
        cards_list = ast.literal_eval(support_cards_str)
        if not isinstance(cards_list, list):
            return []
        
        parsed_tuples = []
        for card_dict in cards_list:
            # Check for 'name' and 'level' keys
            if isinstance(card_dict, dict) and 'name' in card_dict and 'level' in card_dict:
                parsed_tuples.append((card_dict['name'], card_dict['level']))
        
        return parsed_tuples
    except (ValueError, SyntaxError, TypeError):
        # Handle cases where the string is not a valid list literal
        return []

# --- Main Processing ---
try:
    # Load the dataframe
    df = pd.read_csv(input_filename, low_memory=False)
    print(f"Successfully loaded '{input_filename}'.")

    # 1. Define the columns you want to keep
    columns_to_keep = [
        "arena", "game_config_name", "players_0_avgManaCost", "players_0_hashtag", "players_0_score",
        "players_0_stars", "players_0_winner", "players_0_elixirLeaked", "players_0_supportCards",
        'players_0_spells', "players_0_kingTowerHitPoints", "players_0_princessTowersHitPoints",
        "players_1_avgManaCost", "players_1_hashtag", "players_1_score", "players_1_stars",
        "players_1_winner", "players_1_elixirLeaked", "players_1_spells", 'players_1_supportCards',
        "players_1_kingTowerHitPoints", "players_1_princessTowersHitPoints"
    ]

    # Filter out any columns that don't exist in the loaded CSV
    existing_columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    
    # Create the new dataframe
    results_df = df[existing_columns_to_keep].copy()

    # 2. Filter out "TeamVsTeam" rows
    if "game_config_name" in results_df.columns:
        results_df = results_df[results_df["game_config_name"] != "TeamVsTeam"].copy()
        print("Filtered out 'TeamVsTeam' rows.")

    # 3. Apply Spells Transformation (from previous step)
    if 'players_0_spells' in results_df.columns:
        results_df['players_0_spells'] = results_df['players_0_spells'].apply(parse_spells)
        print("Processed 'players_0_spells'.")

    if 'players_1_spells' in results_df.columns:
        results_df['players_1_spells'] = results_df['players_1_spells'].apply(parse_spells)
        print("Processed 'players_1_spells'.")

    # 4. Apply Support Cards Transformation (NEW STEP)
    if 'players_0_supportCards' in results_df.columns:
        results_df['players_0_supportCards'] = results_df['players_0_supportCards'].apply(parse_support_cards)
        print("Processed 'players_0_supportCards'.")

    if 'players_1_supportCards' in results_df.columns:
        results_df['players_1_supportCards'] = results_df['players_1_supportCards'].apply(parse_support_cards)
        print("Processed 'players_1_supportCards'.")

    # 5. Save the preprocessed data
    results_df.to_csv(output_filename, index=False)
    print(f"\nSuccessfully preprocessed all data and saved to '{output_filename}'")

    # Optional: Display info and head to verify the new columns
    print("\n--- DataFrame Info after All Preprocessing ---")
    results_df.info()
    
    print("\n--- Head of Transformed 'supportCards' Columns ---")
    support_cols_to_show = [col for col in ['players_0_supportCards', 'players_1_supportCards'] if col in results_df.columns]
    if support_cols_to_show:
        print(results_df[support_cols_to_show].head())

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")