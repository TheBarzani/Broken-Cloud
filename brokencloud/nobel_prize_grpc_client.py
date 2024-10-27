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
from dotenv import load_dotenv

# Loading variables from .env file
load_dotenv()

class NobelPrizeGRPCClient:
    def __init__(self, host: str = 'localhost', port: int = 50051):
        """Initialize gRPC channel."""
        # Create channel with keepalive options
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
        ]
        
        channel = grpc.insecure_channel(
            f'{host}:{port}',
            options=options
        )
        
        # Wait for channel to be ready
        try:
            grpc.channel_ready_future(channel).result(timeout=60)
            print(f"Successfully connected to {host}:{port}")
        except grpc.FutureTimeoutError:
            print(f"Failed to connect to {host}:{port}")
            raise
            
        self.stub = nobel_prize_pb2_grpc.NobelPrizeServiceStub(channel)

    def count_laureates_by_category_and_years(self, category: str, 
                                            start_year: int, end_year: int) -> int:
        request = nobel_prize_pb2.CategoryYearRequest(
            category=category,
            start_year=start_year,
            end_year=end_year
        )
        try:
            response = self.stub.CountLaureatesByCategoryAndYears(
                request,
                timeout=30  # 30 seconds timeout
            )
            return response.count
        except grpc.RpcError as e:
            print(f"RPC error: {e.details()}")
            return 0

    def count_laureates_by_motivation_keyword(self, keyword: str) -> int:
        request = nobel_prize_pb2.MotivationKeywordRequest(keyword=keyword)
        try:
            response = self.stub.CountLaureatesByMotivationKeyword(
                request,
                timeout=30
            )
            return response.count
        except grpc.RpcError as e:
            print(f"RPC error: {e.details()}")
            return 0

    def get_laureate_details_by_name(self, firstname: str, 
                           surname: str) -> List[Dict[str, str]]:
        request = nobel_prize_pb2.LaureateNameRequest(
            firstname=firstname,
            surname=surname
        )
        try:
            response = self.stub.GetLaureateDetailsByName(
                request,
                timeout=30
            )
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
        grpc_client = NobelPrizeGRPCClient(
            host=os.getenv("GRPC_HOST", "localhost"),
            port= 50051
        )
        cli = NobelPrizeCLI(grpc_client)
        cli.run()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()