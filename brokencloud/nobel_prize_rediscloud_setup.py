# AUTHOR: @TheBarzani
# DESCRIPTION: Simple script to download Novel Prizes Data since year 
#              1901 in JSON format. Filters out the prizes from 2013 
#              to 2023 and addds it to the Redis DB. Creates requested 
#              indexes.
# ASSIGNMENT TASKS: Tasks 1.1 and 1.2            

import requests
import redis
import os
from redis.commands.json.path import Path
from dotenv import load_dotenv
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


# Loading variables from .env file
load_dotenv()

# Constants
API_URL = "https://api.nobelprize.org/v1/prize.json"
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

def fetch_nobel_prize_data(url: str) -> dict | None:
    """
    Fetch Nobel Prize data from the API.
    
    Args:
        url (str): The API URL to fetch data from
        
    Returns:
        dict | None: JSON response or None if request fails
    """
    try:
        response = requests.get(url, timeout=30)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def filter_prize_by_year(data: dict, from_year: int, to_year: int) -> list:
    """
    Filter prizes by year range.
    
    Args:
        data (dict): The complete prize data
        from_year (int): Start year (inclusive)
        to_year (int): End year (inclusive)
        
    Returns:
        list: Filtered list of prizes
    """
    if not data or 'prizes' not in data:
        return []
    return [prize for prize in data['prizes'] 
            if from_year <= int(prize['year']) <= to_year]

def save_to_redis(redis_client: redis.Redis, data: dict, from_year: int, 
                  to_year: int) -> bool:
    """
    Save filtered prize data to Redis.
    
    Args:
        redis_client: Redis client instance
        data (dict): The complete prize data
        from_year (int): Start year
        to_year (int): End year
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        filtered_prizes = filter_prize_by_year(data, from_year, to_year)
        if not filtered_prizes:
            print("No prizes found in the specified year range")
            return False
            
        # Clear existing data before inserting new
        existing_keys = redis_client.keys('prizes:*')
        if existing_keys:
            redis_client.delete(*existing_keys)
            
        for i, prize in enumerate(filtered_prizes, 1):
            key = f'prizes:{i}'
            prize["year"] = int(prize["year"])
            redis_client.json().set(name=key, path=Path.root_path(), obj=prize)
            
        print(f"Successfully saved {len(filtered_prizes)} prizes to Redis")
        return True
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False

def create_search_index(redis_client: redis.Redis) -> bool:
    """
    Create search index for Nobel Prize data.
    
    Args:
        redis_client: Redis client instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Delete existing index if it exists
        try:
            redis_client.ft("prizeIdx").dropindex()
        except redis.ResponseError:
            pass  # Index doesn't exist
        
        schema = (
            NumericField("$.year", as_name="year"),
            TextField("$.category", as_name="category"),
            TextField("$.laureates[*].firstname", as_name="firstname"),
            TextField("$.laureates[*].surname", as_name="surname"),
            TextField("$.laureates[*].motivation", as_name="motivation")
        )

        redis_client.ft("prizeIdx").create_index(
            schema,
            definition=IndexDefinition(
                prefix=["prizes:"],
                index_type=IndexType.JSON
            )
        )
        return True
    except redis.RedisError as e:
        print(f"Error creating search index: {e}")
        return False

def main():
    if not all([REDIS_HOST, REDIS_PORT, REDIS_PASSWORD]):
        print("Missing required Redis configuration in .env file")
        return

    print("Fetching Nobel Prize data...")
    data = fetch_nobel_prize_data(API_URL)
    if not data:
        print("Failed to fetch Nobel Prize data")
        return

    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        redis_client.ping()
        print("Connected to Redis Cloud successfully")

        # Create index first
        if not create_search_index(redis_client):
            return

        # Then save data
        if not save_to_redis(redis_client, data, 2013, 2023):
            return

        # Verify data was indexed
        result = redis_client.ft("prizeIdx").search("*")
        print(f"Found {result.total} documents in index")

        print("Data processing completed successfully")
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")

if __name__ == "__main__":
    main()