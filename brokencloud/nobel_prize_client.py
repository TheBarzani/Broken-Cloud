# AUTHOR: @TheBarzani
# DESCRIPTION: A client application to communicate with the NobleDB.
# DEPENDENCY: Ensure that the sample Noble prize data is added to Redis DB.
#             This can be done using the « noble_redisdb_setup.py » script.   

# TODO: Refactor all the code

import redis
import os
from dotenv import load_dotenv
from redis.commands.search.query import Query
from typing import List, Dict

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

    def get_laureate_details(self, firstname: str, 
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


class NobelPrizeCLI:
    def __init__(self):
        """Initialize CLI with Redis connection from environment variables."""
        
        self.client = NobelPrizeClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )
        
        self.categories = [
            "Physics", "Chemistry", "Peace", "Medicine", 
            "Literature", "Economics"
        ]

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu(self):
        """Display the main menu."""
        self.clear_screen()
        print("\n========== Nobel Prize Query System ==========")
        print("\n1. Count laureates by category and year range")
        print("2. Count laureates by motivation keyword")
        print("3. Find laureate details by name")
        print("4. Exit")
        print("\n=============================================")

    def get_valid_year(self, prompt: str) -> int:
        """Get a valid year input from user."""
        while True:
            try:
                year = int(input(prompt))
                if 2013 <= year <= 2023:
                    return year
                print("Year must be between 2013 and 2023")
            except ValueError:
                print("Please enter a valid year")

    def query_category_and_years(self):
        """Handle category and year range query."""
        self.clear_screen()
        print("\n========= Count Laureates by Category and Years =========\n")
        
        # Display available categories
        print("Available categories:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category}")
        
        # Get category choice
        while True:
            try:
                choice = int(input("\nSelect category number: "))
                if 1 <= choice <= len(self.categories):
                    category = self.categories[choice-1]
                    break
                print("Invalid selection")
            except ValueError:
                print("Please enter a valid number")
        
        # Get year range
        start_year = self.get_valid_year("\nEnter start year (2013-2023): ")
        while True:
            end_year = self.get_valid_year("Enter end year (2013-2023): ")
            if end_year >= start_year:
                break
            print("End year must be greater than or equal to start year")
        
        # Execute query and display results
        count = self.client.count_laureates_by_category_and_years(
            category.lower(), start_year, end_year)
        print(f"\nFound {count} laureates in {category} between {start_year}-{end_year}")
        input("\nPress Enter to continue...")

    def query_motivation_keyword(self):
        """Handle motivation keyword query."""
        self.clear_screen()
        print("\n========= Count Laureates by Motivation Keyword =========\n")
        
        keyword = input("Enter keyword to search in motivations: ")
        count = self.client.count_laureates_by_motivation_keyword(keyword)
        print(f"\nFound {count} laureates with '{keyword}' in their motivation")
        input("\nPress Enter to continue...")

    def query_laureate_details(self):
        """Handle laureate name query."""
        self.clear_screen()
        print("\n========= Find Laureate Details by Name =========\n")
        
        firstname = input("Enter first name: ")
        surname = input("Enter last name: ")
        
        prizes = self.client.get_laureate_details(firstname, surname)
        
        if prizes:
            print(f"\nFound {len(prizes)} prize(s) for {firstname} {surname}:")
            for i, prize in enumerate(prizes, 1):
                print(f"\nPrize {i}:")
                print(f"Year: {prize['year']}")
                print(f"Category: {prize['category']}")
                print(f"Motivation: {prize['motivation']}")
        else:
            print(f"\nNo prizes found for {firstname} {surname}")
        
        input("\nPress Enter to continue...")

    def run(self):
        """Run the CLI menu loop."""
        while True:
            self.print_menu()
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.query_category_and_years()
            elif choice == '2':
                self.query_motivation_keyword()
            elif choice == '3':
                self.query_laureate_details()
            elif choice == '4':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")

def main():
    """Main entry point of the application."""
    try:
        cli = NobelPrizeCLI()
        cli.run()
    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        print("Please check your Redis credentials in the .env file")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

