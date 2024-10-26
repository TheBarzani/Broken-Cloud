# AUTHOR: @TheBarzani
# DESCRIPTION: A cli application interface for NobelDB.   
# ASSIGNMENT TASKS: Tasks 1.3 and 2.3  

import os

class NobelPrizeCLI:
    def __init__(self, client):
        """Initialize CLI with Redis connection from environment variables."""
        
        self.client = client
        
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
        
        prizes = self.client.get_laureate_details_by_name(firstname, surname)
        
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
