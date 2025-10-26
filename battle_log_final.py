import pandas as pd
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time


def flatten_dict(d, parent_key="", sep="_"):
    """
    Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: String to prepend to dictionary keys
        sep: Separator between parent and child keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            # Recursively flatten nested dictionaries
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flatter_battle_log(dict_battle: dict) -> dict:
    new_dict = {}

    dict_keys = ["game_config"]
    list_keys = ["players"]
    remove_keys = []
    for key in dict_battle.keys():
        if key in dict_keys:
            flattened = flatten_dict(dict_battle[key], parent_key=key)
            new_dict.update(flattened)
        elif key in list_keys:
            for i in range(len(dict_battle[key])):
                flattened = flatten_dict(dict_battle[key][i], parent_key=f"{key}_{i}")
                new_dict.update(flattened)

        elif key in remove_keys:
            continue
        else:
            new_dict[key] = dict_battle[key]

    return new_dict


def fetch_api_data(
    id: str,
    url: str = "https://stats-royale-api-js-beta-z2msk5bu3q-uk.a.run.app/profile/",
    headers: Dict = None,
) -> Dict:
    """Fetch data from a single API endpoint"""
    try:
        request_url = f"{url}{id}"
        print(f"Fetching: {request_url}")
        response = requests.get(request_url, headers=headers, timeout=10)
        response.raise_for_status()
        # if response.status_code == 200:
        #     matches = response.json()['matches']
        #     flattened_matches = [flatten_dict(match) for match in matches]
        #     return {"id": id, "flat_matches": flattened_matches, "status": "success"}
        matches = response.json()["matches"]
        flattened_matches = [flatter_battle_log(match) for match in matches]
        df_matches = pd.DataFrame(flattened_matches)

        return id, "success", df_matches

    except Exception as e:
        print("error", e)
        return id, "failed", None


def parallel_api_calls(
    ids: List[str], max_workers: int = 5, headers: Dict = None
) -> pd.DataFrame:
    """
    Make parallel API calls

    Args:
        urls: List of API URLs to call
        max_workers: Number of parallel workers (default: 5)
        headers: Optional headers for API requests

    Returns:
        List of results from all API calls
    """
    df = pd.DataFrame()
    completed = 0
    failed_id = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_id = {executor.submit(fetch_api_data, id): id for id in ids}
        results = pd.DataFrame()
        # Process completed tasks
        for future in as_completed(future_to_id):
            result = future.result()
            if result[1] == "failed":
                print(f"Failed to fetch data for ID: {future_to_id[future]}")
                failed_id.append(future_to_id[future])
                continue

            results = pd.concat([results, result[2]], ignore_index=True)
            time.sleep(0.2)  # Slight delay to avoid overwhelming the server
            print(f"Completed: {result[0]} - Status: {result[1]}")
            completed += 1
            if completed % 10 == 0 or completed == len(ids):
                print(f"Progress: {completed}/{len(ids)} completed")
    df = pd.DataFrame(results)
    return df, failed_id


def save_to_csv(data: pd.DataFrame, filename: str):
    """Save DataFrame to CSV file"""
    data.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def battle_log_from_json(
    json_file_path: str,
    csv_file_path: str,
    index_tuple: tuple = None,
    csv_file_path_failed: str = "failed_ids.csv",
):
    """Load battle log data from a JSON file and save to CSV"""
    with open(json_file_path, "r", errors="ignore") as file:
        data = json.load(file)

    players_json_unpacked = data["players"]
    # players_json_unpacked is a list of dicts with each dict with details of players with id being with the key "tag"

    players_json_unpacked_ids = [player["tag"] for player in players_json_unpacked]
    if index_tuple:
        players_json_unpacked_ids = players_json_unpacked_ids[
            index_tuple[0] : index_tuple[1]
        ]
    else:
        print(len(players_json_unpacked_ids))
        players_json_unpacked_ids = players_json_unpacked_ids[
            :100
        ]  # Limit to first 100 IDs for testing

    # Make parallel API calls
    results_df, failed_ids = parallel_api_calls(
        players_json_unpacked_ids, max_workers=30
    )
    # Save to CSV

    save_to_csv(results_df, csv_file_path)

    if failed_ids:
        print(f"Failed to fetch data for IDs: {failed_ids}")
    # Append new failed ids to file, avoid writing duplicates already present
        try:
            with open(csv_file_path_failed, "a+", encoding="utf-8") as f:
                f.seek(0)
                existing = {line.strip() for line in f if line.strip()}
                to_write = [str(i) for i in failed_ids if str(i) not in existing]
                if to_write:
                    f.write("\n".join(to_write) + "\n")
        except Exception as e:
            print("Could not write failed ids:", e)


if __name__ == "__main__":
    # Define your Player ids
    # ids = ["2G2L9PRUP"]

    # # Optional: Add headers if needed (e.g., API key)
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    # }

    # # Make parallel API calls
    # results_df = parallel_api_calls(ids, max_workers=10, headers=headers)

    # # Save to CSV
    # save_to_csv(results_df, "battle_log_data_neo.csv")
    json_path = r"./scraped_ids/clash_royale_uniform.json"
    battle_log_from_json(json_path, "battle_log_full_batch_trail.csv")
