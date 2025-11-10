import json
import pandas as pd
import requests

def scrape_card_data_from_json(json_file_path, output_file='card_database.csv'):
    """
    Scrape card data from Clash Royale game data JSON file with your specific structure
    """
    
    print("Loading game data JSON...")
    
    try:
        # Load the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            game_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON file")
        return
    
    print("Extracting card data from spells section...")
    
    card_data = []
    
    # Navigate to the spells section in the items
    if 'items' in game_data and 'spells' in game_data['items']:
        spells_list = game_data['items']['spells']
        print(f"Found {len(spells_list)} spells in the JSON")
    else:
        print("Error: Could not find 'items -> spells' in JSON structure")
        print("Available keys in items:", list(game_data.get('items', {}).keys()))
        return
    
    for card in spells_list:
        try:
            card_info = {}
            
            # English Name (directly available)
            if 'englishName' in card:
                card_info['englishName'] = card['englishName']
            elif 'name' in card:
                card_info['englishName'] = card['name']
            else:
                print(f"Skipping card without name: {card}")
                continue
            
            # ID
            if 'id' in card:
                card_info['id'] = card['id']
            else:
                card_info['id'] = card_info['englishName']  # Use name as fallback ID
            
            # Evolution Status (1 if evolvedSpellsData exists, else 0)
            if 'evolvedSpellsData' in card and card['evolvedSpellsData'] is not None:
                card_info['is_evo'] = 1
            else:
                card_info['is_evo'] = 0
            
            # Elixir Cost from manaCost
            if 'manaCost' in card:
                card_info['elixir_cost'] = card['manaCost']
            else:
                card_info['elixir_cost'] = None  # Mark as unknown
            
            # Rarity
            if 'rarity' in card:
                rarity = card['rarity']
                # Standardize rarity names
                if rarity.lower() in ['common', 'c']:
                    card_info['rarity'] = 'Common'
                elif rarity.lower() in ['rare', 'r']:
                    card_info['rarity'] = 'Rare'
                elif rarity.lower() in ['epic', 'e']:
                    card_info['rarity'] = 'Epic'
                elif rarity.lower() in ['legendary', 'l']:
                    card_info['rarity'] = 'Legendary'
                elif rarity.lower() in ['champion', 'ch']:
                    card_info['rarity'] = 'Champion'
                else:
                    card_info['rarity'] = rarity  # Keep original if unknown
            else:
                card_info['rarity'] = 'Unknown'
            
            # Icon from iconFile
            if 'iconFile' in card:
                card_info['icon_file'] = card['iconFile']
            else:
                card_info['icon_file'] = ''
            
            # Additional useful fields from your structure
            if 'tid' in card:
                card_info['tid'] = card['tid']
            else:
                card_info['tid'] = ''
            
            if 'unlockArena' in card:
                card_info['unlock_arena'] = card['unlockArena']
            else:
                card_info['unlock_arena'] = ''
            
            if 'tribe' in card:
                card_info['tribe'] = card['tribe']
            else:
                card_info['tribe'] = ''
            
            # Evolution details if available
            if card_info['is_evo'] == 1 and 'evolvedSpellsData' in card:
                evo_data = card['evolvedSpellsData']
                if 'name' in evo_data:
                    card_info['evo_name'] = evo_data['name']
                if 'iconFile' in evo_data:
                    card_info['evo_icon_file'] = evo_data['iconFile']
            else:
                card_info['evo_name'] = ''
                card_info['evo_icon_file'] = ''
            
            card_data.append(card_info)
            
        except Exception as e:
            print(f"Error processing card {card.get('englishName', 'Unknown')}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(card_data)
    
    # Remove duplicates based on englishName
    df = df.drop_duplicates(subset=['englishName'], keep='first')
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"\nScraping complete!")
    print(f"Total cards found: {len(df)}")
    print(f"EVO cards: {df['is_evo'].sum()}")
    print(f"NON-EVO cards: {len(df) - df['is_evo'].sum()}")
    
    # Print summary by rarity
    print("\nCards by rarity:")
    rarity_counts = df['rarity'].value_counts()
    for rarity, count in rarity_counts.items():
        print(f"  {rarity}: {count}")
    
    # Print summary by elixir cost
    print("\nCards by elixir cost:")
    elixir_counts = df['elixir_cost'].value_counts().sort_index()
    for elixir, count in elixir_counts.items():
        print(f"  {elixir} elixir: {count}")
    
    # Print EVO cards
    evo_cards = df[df['is_evo'] == 1]['englishName'].tolist()
    if evo_cards:
        print(f"\nEVO cards found: {', '.join(evo_cards)}")
    
    print(f"\nData saved to: {output_file}")
    
    return df

def create_enhanced_card_database(json_file_path, output_file='enhanced_card_database.csv'):
    """
    Create an enhanced card database with more detailed information
    """
    print("Creating enhanced card database...")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            game_data = json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    if 'items' not in game_data or 'spells' not in game_data['items']:
        print("Error: Could not find spells in JSON")
        return
    
    spells_list = game_data['items']['spells']
    enhanced_data = []
    
    for card in spells_list:
        try:
            card_info = {}
            
            # Basic identification
            card_info['englishName'] = card.get('englishName', card.get('name', ''))
            card_info['id'] = card.get('id', '')
            card_info['tid'] = card.get('tid', '')
            
            # Evolution information
            card_info['is_evo'] = 1 if card.get('evolvedSpellsData') else 0
            if card_info['is_evo'] == 1:
                evo_data = card['evolvedSpellsData']
                card_info['evo_englishName'] = evo_data.get('name', '')
                card_info['evo_icon_file'] = evo_data.get('iconFile', '')
            else:
                card_info['evo_englishName'] = ''
                card_info['evo_icon_file'] = ''
            
            # Game stats
            card_info['elixir_cost'] = card.get('manaCost', None)
            card_info['rarity'] = card.get('rarity', 'Unknown')
            card_info['icon_file'] = card.get('iconFile', '')
            card_info['unlock_arena'] = card.get('unlockArena', '')
            card_info['tribe'] = card.get('tribe', '')
            card_info['type'] = card.get('tidType', '')  # Character, Building, etc.
            
            # Character data if available
            if 'summonCharacterData' in card:
                char_data = card['summonCharacterData']
                card_info['hitpoints'] = char_data.get('hitpoints', None)
                card_info['damage'] = char_data.get('damage', None)
                card_info['speed'] = char_data.get('speed', None)
                card_info['deploy_time'] = char_data.get('deployTime', None)
                card_info['range'] = char_data.get('sightRange', None)
            else:
                card_info['hitpoints'] = None
                card_info['damage'] = None
                card_info['speed'] = None
                card_info['deploy_time'] = None
                card_info['range'] = None
            
            enhanced_data.append(card_info)
            
        except Exception as e:
            print(f"Error processing card {card.get('englishName', 'Unknown')}: {e}")
            continue
    
    df = pd.DataFrame(enhanced_data)
    df = df.drop_duplicates(subset=['englishName'], keep='first')
    df.to_csv(output_file, index=False)
    
    print(f"Enhanced database created with {len(df)} cards")
    print(f"Saved to: {output_file}")
    
    return df

def create_card_mapping_file(json_file_path, output_file='card_id_mapping.csv'):
    """
    Create a simple mapping file for card names to IDs and evolution status
    Useful for merging with your battle data
    """
    print("Creating card mapping file...")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            game_data = json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    if 'items' not in game_data or 'spells' not in game_data['items']:
        print("Error: Could not find spells in JSON")
        return
    
    spells_list = game_data['items']['spells']
    mapping_data = []
    
    for card in spells_list:
        try:
            mapping = {}
            mapping['englishName'] = card.get('englishName', card.get('name', ''))
            mapping['id'] = card.get('id', '')
            mapping['is_evo'] = 1 if card.get('evolvedSpellsData') else 0
            mapping['elixir_cost'] = card.get('manaCost', None)
            mapping['rarity'] = card.get('rarity', 'Unknown')
            mapping['icon_file'] = card.get('iconFile', '')
            
            mapping_data.append(mapping)
            
        except Exception as e:
            print(f"Error processing card: {e}")
            continue
    
    df = pd.DataFrame(mapping_data)
    df = df.drop_duplicates(subset=['englishName'], keep='first')
    df.to_csv(output_file, index=False)
    
    print(f"Card mapping file created with {len(df)} entries")
    print(f"Saved to: {output_file}")
    
    return df

# Main execution
if __name__ == "__main__":
    # Replace with your actual JSON file path
    json_file_path = "gamedata-v4.json"
    
    print("🚀 Starting Clash Royale Card Data Scraper")
    print("=" * 50)
    
    # Method 1: Basic card database
    print("\n1. Creating basic card database...")
    basic_df = scrape_card_data_from_json(json_file_path, 'card_database.csv')
    
    # Method 2: Enhanced database with character stats
    print("\n2. Creating enhanced card database...")
    enhanced_df = create_enhanced_card_database(json_file_path, 'enhanced_card_database.csv')
    
    # Method 3: Simple mapping file for data merging
    print("\n3. Creating card mapping file...")
    mapping_df = create_card_mapping_file(json_file_path, 'card_id_mapping.csv')
    
    print("\n" + "=" * 50)
    print("✅ All scraping operations completed!")
    
    if basic_df is not None:
        print(f"\nSample of basic database:")
        print(basic_df.head(10)[['englishName', 'id', 'is_evo', 'elixir_cost', 'rarity']])
        
        # Show EVO cards specifically
        evo_cards = basic_df[basic_df['is_evo'] == 1]
        if len(evo_cards) > 0:
            print(f"\nEVO Cards found ({len(evo_cards)}):")
            for _, card in evo_cards.iterrows():
                print(f"  - {card['englishName']} (ID: {card['id']})")