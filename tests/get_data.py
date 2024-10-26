
# AUTHOR: @TheBarzani
# DESCRIPTION: Simple script to download Novel Prizes Data since year 1901 
#              in JSON format.

import requests
import json
import os

# URL for the Nobel Prize API
API_URL = "https://api.nobelprize.org/v1/prize.json"
OUTPUT_FILE = "prize.json"

def fetch_nobel_prize_data(url):
    try:
        # Send a GET request to fetch the data
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses 
        return response.json()  # Return the JSON content of the response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None  # Return None if there's an error

def save_to_json_file(data, output_file):
    try:
        # Write the fetched data to a file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {output_file}")
    except IOError as io_err:
        print(f"File I/O error occurred: {io_err}")

def main():
    # Fetch the Nobel Prize data
    print("Fetching Nobel Prize data...")
    data = fetch_nobel_prize_data(API_URL)
    
    if data:
        # If data is successfully fetched, save it to a file
        save_to_json_file(data, OUTPUT_FILE)
    else:
        print("Failed to fetch Nobel Prize data.")

if __name__ == "__main__":
    main()