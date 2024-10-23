# AUTHOR: @SmileBar
# DESCRIPTION: Simple script to download Novel Prizes Data since year 1901 in JSON format
#              and add to it REDIS cloud database.

import requests
import redis
import json
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# Nobel Prize API URL
API_URL = "https://api.nobelprize.org/v1/prize.json"

# Redis connection parameters (replace with your Redis Cloud credentials)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

def fetch_nobel_prize_data(url):
    try:
        # Send GET request to fetch data from Nobel Prize API
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

def save_to_redis(redis_client, data):
    try:
        # Convert the data to a JSON string
        json_data = json.dumps(data)
        
        # Store the data in Redis with the key 'nobel_prizes'
        redis_client.set('nobel_prizes', json_data)
        print("Data successfully saved to Redis.")
    except redis.RedisError as redis_err:
        print(f"Redis error occurred: {redis_err}")

def main():
    # Fetch Nobel Prize data from API
    print("Fetching Nobel Prize data...")
    data = fetch_nobel_prize_data(API_URL)

    if data:
        # Establish connection to Redis Cloud
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True  # Ensures string encoding
        )

        try:
            # Check if the Redis connection is successful
            redis_client.ping()
            print("Connected to Redis Cloud successfully.")
            
            # Save the fetched data to Redis
            save_to_redis(redis_client, data)
        except redis.ConnectionError as conn_err:
            print(f"Could not connect to Redis: {conn_err}")
    else:
        print("Failed to fetch Nobel Prize data.")

if __name__ == "__main__":
    main()