# AUTHOR: @TheBarzani
# DESCRIPTION: A server application to handle gRPC service/gateway.
#   
# ASSIGNMENT TASKS: Task 2.3
#    
# TODO: Refactor and comment

import os
import grpc
from concurrent import futures
import time
from redis.commands.search.query import Query
from nobel_prize_pb2 import (
    LaureateCountResponse,
    LaureateDetailsResponse,
    LaureateDetail
)
import nobel_prize_pb2_grpc
from nobel_prize_client import NobelPrizeClient  # Import the Redis client class
from dotenv import load_dotenv

# Loading variables from .env file
load_dotenv()

# Constants
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


class NobelPrizeService(nobel_prize_pb2_grpc.NobelPrizeServiceServicer):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str):
        """Initialize Redis connection."""
        self.client = NobelPrizeClient(
            host=redis_host,
            port=redis_port,
            password=redis_password
        )

    def CountLaureatesByCategoryAndYears(self, request, context):
        """
        Implement Service 1: Count laureates by category and year range
        """
        try:
            count = self.client.count_laureates_by_category_and_years(
                request.category, request.start_year, request.end_year
            )
            return LaureateCountResponse(count=count, message="Success")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def CountLaureatesByMotivationKeyword(self, request, context):
        """
        Implement Service 2: Count laureates by motivation keyword
        """
        try:
            count = self.client.count_laureates_by_motivation_keyword(request.keyword)
            return LaureateCountResponse(count=count, message="Success")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetLaureateDetailsByName(self, request, context):
        """
        Implement Query 3: Get laureate details by name
        """
        try:
            laureate_details = self.client.get_laureate_details_by_name(request.firstname, request.surname)
            details = [
                LaureateDetail(year=detail['year'], category=detail['category'], motivation=detail['motivation'])
                for detail in laureate_details
            ]
            return LaureateDetailsResponse(details=details, message=("Success" if laureate_details else "No prizes found"))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

def serve(redis_host: str, redis_port: int, redis_password: str):
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nobel_prize_pb2_grpc.add_NobelPrizeServiceServicer_to_server(
        NobelPrizeService(redis_host, redis_port, redis_password), 
        server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve(
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT,
        redis_password=REDIS_PASSWORD
    )





