# AUTHOR: @TheBarzani
# DESCRIPTION: A gRPC client program to communicate with gRPC Service (Gateway).
#   
# ASSIGNMENT TASKS: Task 2.3  
# 
# TODO: Refactor

# nobel_prize_client.py
import grpc
import os
from typing import List, Dict

# Import generated protocol buffer code
import nobel_prize_pb2
import nobel_prize_pb2_grpc
from nobel_prize_cli import NobelPrizeCLI

class NobelPrizeGRPCClient:
    def __init__(self, host: str = 'localhost', port: int = 50051):
        """Initialize gRPC channel and client stub."""
        channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = nobel_prize_pb2_grpc.NobelPrizeServiceStub(channel)

    def count_laureates_by_category_and_years(self, category: str, 
                                            start_year: int, end_year: int) -> int:
        """Query laureate count by category and year range via gRPC."""
        request = nobel_prize_pb2.CategoryYearRequest(
            category=category,
            start_year=start_year,
            end_year=end_year
        )
        try:
            response = self.stub.CountLaureatesByCategoryAndYears(request)
            return response.count
        except grpc.RpcError as e:
            print(f"RPC error: {e.details()}")
            return 0

    def count_laureates_by_motivation_keyword(self, keyword: str) -> int:
        """Query laureate count by motivation keyword via gRPC."""
        request = nobel_prize_pb2.MotivationKeywordRequest(keyword=keyword)
        try:
            response = self.stub.CountLaureatesByMotivationKeyword(request)
            return response.count
        except grpc.RpcError as e:
            print(f"RPC error: {e.details()}")
            return 0

    def get_laureate_details_by_name(self, firstname: str, 
                           surname: str) -> List[Dict[str, str]]:
        """Query laureate details by name via gRPC."""
        request = nobel_prize_pb2.LaureateNameRequest(
            firstname=firstname,
            surname=surname
        )
        try:
            response = self.stub.GetLaureateDetailsByName(request)
            return [
                {
                    'year': detail.year,
                    'category': detail.category,
                    'motivation': detail.motivation
                }
                for detail in response.details
            ]
        except grpc.RpcError as e:
            print(f"RPC error: {e.details()}")
            return []


def main():
    """Main entry point of the application."""
    try:
        # TODO: Deploy to cloud and change host
        grpc_client = NobelPrizeGRPCClient(host = "3.16.56.165")
        cli = NobelPrizeCLI(grpc_client)
        cli.run()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()