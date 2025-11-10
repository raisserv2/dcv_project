import requests
import json
import os
from urllib.parse import urljoin

# Configuration
GAMEDATA_URL = "https://cdn.statsroyale.com/gamedata-v4.json"
BASE_ICON_URL = "https://cdn.statsroyale.com/v6/cards/full_b/"
TARGET_CARDS = [
    'Mega Minion', 'Barbarians', 'Giant', 'Goblin Hut', 'Spear Goblins', 'Valkyrie', 
    'Knight', 'Mini P.E.K.K.A', 'Cannon', 'Tombstone', 'Bomber', 'Skeleton Army', 
    'Musketeer', 'Battle Ram', 'Fireball', 'Goblin Cage', 'Wizard', 'Minions', 
    'Witch', 'Skeleton Dragons', 'Mortar', 'Bats', 'Archers', 'Arrows', 'Skeletons', 
    'Royal Ghost', 'Hog Rider', 'Rocket', 'Zap', 'Flying Machine', 'Goblins', 
    'Inferno Tower', 'Bomb Tower', 'Fire Spirit', 'Electro Spirit', 'Baby Dragon', 
    'Goblin Barrel', 'Three Musketeers', 'P.E.K.K.A', 'Goblin Gang', 'Dart Goblin', 
    'Electro Dragon', 'Balloon', 'Vines', 'Prince', 'Mirror', 'Royal Hogs', 
    'Mega Knight', 'Sparky', 'Clone', 'X-Bow', 'Goblin Curse', 'Miner', 
    'Inferno Dragon', 'Suspicious Bush', 'Elixir Golem', 'Princess', 'The Log', 
    'Ice Wizard', 'Royal Recruits', 'Skeleton Barrel', 'Giant Skeleton', 'Skeleton King', 
    'Void', 'Night Witch', 'Lumberjack', 'Royal Giant', 'Lightning', 'Fisherman', 
    'Giant Snowball', 'Ice Spirit', 'Guards', 'Minion Horde', 'Electro Giant', 
    'Hunter', 'Zappies', 'Dark Prince', 'Barbarian Barrel', 'Tesla', 'Lava Hound', 
    'Tornado', 'Poison', 'Freeze', 'Executioner', 'Royal Delivery', 'Phoenix', 
    'Mother Witch', 'Bowler', 'Ram Rider', 'Firecracker', 'Graveyard', 'Battle Healer', 
    'Bandit', 'Rage', 'Elite Barbarians', 'Magic Archer', 'Rune Giant', 'Berserker', 
    'Rascals', 'Goblin Demolisher', 'Goblin Giant', 'Electro Wizard', 'Golem', 
    'Ice Golem', 'Wall Breakers', 'Goblin Machine', 'Furnace', 'Cannon Cart', 
    'Earthquake', 'Archer Queen', 'Golden Knight', 'Barbarian Hut', 'Goblin Drill', 
    'Heal Spirit', 'Mighty Miner', 'Little Prince', 'Elixir Collector', 'Boss Bandit', 
    'Goblinstein', 'Monk', 'Spirit Empress'
]

# Create directories for saving icons
os.makedirs("card_icons", exist_ok=True)
os.makedirs("evo_card_icons", exist_ok=True)

def sanitize_filename(name):
    """Sanitize card names for use as filenames"""
    return name.replace(' ', '_').replace('.', '').replace('/', '_')

def download_image(url, filename):
    """Download an image from URL and save to filename"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✓ Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def convert_to_evo_id(card_id):
    """Convert normal card ID to evolution card ID by replacing first digit 2 with 3"""
    card_id_str = str(card_id)
    if card_id_str.startswith('2'):
        return '3' + card_id_str[1:]
    return card_id_str

def main():
    print("Fetching game data...")
    
    try:
        # Download game data
        response = requests.get(GAMEDATA_URL, timeout=30)
        response.raise_for_status()
        game_data = response.json()
        
        # Extract spells/cards data
        spells = game_data.get('items', {}).get('spells', [])
        
        if not spells:
            print("No spells data found in game data!")
            return
        
        print(f"Found {len(spells)} total cards in game data")
        
        # Filter cards to only include target cards
        target_cards = []
        for card in spells:
            english_name = card.get('englishName')
            if english_name in TARGET_CARDS:
                target_cards.append(card)
        
        print(f"Filtered to {len(target_cards)} target cards")
        
        # Download icons
        downloaded_count = 0
        evo_downloaded_count = 0
        
        for card in target_cards:
            english_name = card.get('englishName')
            card_id = card.get('id')
            has_evo = 'evolvedSpellsData' in card
            
            if not english_name or not card_id:
                print(f"Skipping card with missing data: {card}")
                continue
            
            print(f"\nProcessing: {english_name} (ID: {card_id})")
            
            # Download normal card icon
            normal_filename = f"card_icons/{sanitize_filename(english_name)}.webp"
            normal_url = f"{BASE_ICON_URL}{card_id}.webp"
            
            if download_image(normal_url, normal_filename):
                downloaded_count += 1
            
            # Download evolution icon if available
            if has_evo:
                evo_id = convert_to_evo_id(card_id)
                evo_filename = f"evo_card_icons/{sanitize_filename(english_name)}_Evolution.webp"
                evo_url = f"{BASE_ICON_URL}{evo_id}_active.webp"
                
                print(f"Evolution URL: {evo_url}")
                
                if download_image(evo_url, evo_filename):
                    evo_downloaded_count += 1
        
        print(f"\nDownload Summary:")
        print(f"Normal card icons: {downloaded_count}/{len(target_cards)}")
        print(f"Evolution card icons: {evo_downloaded_count}")
        print(f"Total downloaded: {downloaded_count + evo_downloaded_count}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing game data JSON: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()