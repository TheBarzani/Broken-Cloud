# AUTHOR: @TheBarzani
# DESCRIPTION: A client application to communicate with the NobleDB.
# DEPENDENCY: Ensure that the sample Noble prize data is added to Redis DB.
#             This can be done using the « noble_redisdb_setup.py » script.   
# ASSIGNMENT TASKS: Tasks 1.3   
# 
# TODO: Refactor

import redis
import os
from dotenv import load_dotenv
from redis.commands.search.query import Query
from typing import List, Dict
from nobel_prize_cli import NobelPrizeCLI

# Loading variables from .env file
load_dotenv()

# Constants
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

class NobelPrizeClient:
    def __init__(self, host: str, port: int, password: str):
        """Initialize Redis connection with search capabilities."""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        self.search_idx = self.redis_client.ft("prizeIdx")
        # TODO: add some exception handling so that it can check if data exists

    def count_laureates_by_category_and_years(self, category: str, start_year: 
                                              int, end_year: int) -> int:
        """
        Count total number of laureates in a given category between specific 
        years.
        
        Args:
            category: Prize category (e.g., 'Physics', 'Chemistry')
            start_year: Starting year (>= 2013)
            end_year: Ending year (<= 2023)
            
        Returns:
            Total number of laureates found
        """
        # Validate year range
        if not (2013 <= start_year <= end_year <= 2023):
            raise ValueError("Years must be between 2013 and 2023")

        # Construct query
        query_str = (
            f"@category:{category} @year:[{start_year} {end_year}]"
        )
        
        try:
            # Execute search
            result = self.search_idx.search(Query(query_str))
            
            # Count laureates from results
            total_laureates = 0
            for doc in result.docs:
                prize_data = self.redis_client.json().get(doc.id)
                if 'laureates' in prize_data:
                    total_laureates += len(prize_data['laureates'])
            
            return total_laureates
        
        except redis.ResponseError as e:
            print(f"Search error: {e}")
            return 0

    def count_laureates_by_motivation_keyword(self, keyword: str) -> int:
        """
        Count laureates whose motivation contains a specific keyword.
        
        Args:
            keyword: Word or phrase to search in motivations
            
        Returns:
            Total number of laureates with matching motivations
        """
        # Construct query for motivation field
        query_str = f'@motivation:"{keyword}"'
        
        try:
            # Execute search
            result = self.search_idx.search(Query(query_str))
            
            # Count laureates from matching results
            total_laureates = 0
            for doc in result.docs:
                prize_data = self.redis_client.json().get(doc.id)
                if 'laureates' in prize_data:
                    # Only count laureates whose motivation matches the keyword
                    total_laureates += sum(
                        1 for laureate in prize_data['laureates']
                        if keyword.lower() in laureate.get('motivation',
                                                            '').lower()
                    )
            
            return total_laureates
            
        except redis.ResponseError as e:
            print(f"Search error: {e}")
            return 0

    def get_laureate_details_by_name(self, firstname: str, 
                             surname: str) -> List[Dict[str, str]]:
        """
        Find prize details for a laureate by their full name.
        
        Args:
            firstname: Laureate's first name
            surname: Laureate's last name
            
        Returns:
            List of dictionaries containing year, category, and motivation 
            for each prize
        """
        # Construct query to match both names
        query_str = f'@firstname:"{firstname}" @surname:"{surname}"'
        
        try:
            # Execute search
            result = self.search_idx.search(Query(query_str))
            
            # Extract relevant details
            laureate_prizes = []
            for doc in result.docs:
                prize_data = self.redis_client.json().get(doc.id)
                
                # Find matching laureate in the prize data
                for laureate in prize_data.get('laureates', []):
                    if (laureate.get('firstname', '').lower() == 
                        firstname.lower() and 
                        laureate.get('surname', '').lower() == surname.lower()):
                        laureate_prizes.append({
                            'year': prize_data['year'],
                            'category': prize_data['category'],
                            'motivation': laureate.get('motivation', 
                                                       'No motivation provided')
                        })
            
            return laureate_prizes
            
        except redis.ResponseError as e:
            print(f"Search error: {e}")
            return []


def main():
    """Main entry point of the application."""
    try:
        client = NobelPrizeClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )
        cli = NobelPrizeCLI(client=client)
        cli.run()
    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        print("Please check your Redis credentials in the .env file")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

