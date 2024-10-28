
# AUTHOR: @TheBarzani
# DESCRIPTION: Simple script that runs the client from a local computer for 100 
#              times to each of three queries and measure the end-toend delay. 

import time
import csv
from typing import List
from nobel_prize_grpc_client import NobelPrizeGRPCClient 

def measure_query_delay(client: NobelPrizeGRPCClient, query_function: str, *args) -> float:
    """Measures the execution time of a gRPC query in milliseconds."""
    start_time = time.time()
    
    # Call the specified query function with arguments
    if query_function == "count_laureates_by_category_and_years":
        client.count_laureates_by_category_and_years(*args)
    elif query_function == "count_laureates_by_motivation_keyword":
        client.count_laureates_by_motivation_keyword(*args)
    elif query_function == "get_laureate_details_by_name":
        client.get_laureate_details_by_name(*args)
    
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds

def run_queries(client: NobelPrizeGRPCClient, num_runs: int = 100):
    """Runs all queries the specified number of times and records delays in milliseconds."""
    # Lists to store delays
    category_year_delays = []
    motivation_keyword_delays = []
    name_details_delays = []

    for _ in range(num_runs):
        # Measure delays for each query in milliseconds
        category_year_delay = measure_query_delay(client, "count_laureates_by_category_and_years", "Physics", 2015, 2020)
        category_year_delays.append(category_year_delay)

        motivation_keyword_delay = measure_query_delay(client, "count_laureates_by_motivation_keyword", "Peace")
        motivation_keyword_delays.append(motivation_keyword_delay)

        name_details_delay = measure_query_delay(client, "get_laureate_details_by_name", "Alain", "Aspect")
        name_details_delays.append(name_details_delay)

    # Save results to CSV files in milliseconds
    save_to_csv("category_year_delays.csv", category_year_delays)
    save_to_csv("motivation_keyword_delays.csv", motivation_keyword_delays)
    save_to_csv("name_details_delays.csv", name_details_delays)

def save_to_csv(filename: str, data: List[float]):
    """Saves a list of delays to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Delay (milliseconds)'])  # Header
        for delay in data:
            writer.writerow([delay])

if __name__ == "__main__":
    grpc_client = NobelPrizeGRPCClient(host="3.16.56.165") 
    run_queries(grpc_client)
