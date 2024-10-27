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
from nobel_prize_client import NobelPrizeClient
from dotenv import load_dotenv

# Loading variables from .env file
load_dotenv()

# Constants
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
SERVER_PORT = os.getenv("PORT", "50051")

class NobelPrizeService(nobel_prize_pb2_grpc.NobelPrizeServiceServicer):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str):
        """Initialize Redis connection."""
        self.client = NobelPrizeClient(
            host=redis_host,
            port=redis_port,
            password=redis_password
        )
        print(f"Initialized connection to Redis at {redis_host}:{redis_port}")

    def CountLaureatesByCategoryAndYears(self, request, context):
        try:
            print(f"Processing request for category {request.category}")
            count = self.client.count_laureates_by_category_and_years(
                request.category, request.start_year, request.end_year
            )
            return LaureateCountResponse(count=count, message="Success")
        except Exception as e:
            print(f"Error in CountLaureatesByCategoryAndYears: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def CountLaureatesByMotivationKeyword(self, request, context):
        try:
            print(f"Processing request for keyword: {request.keyword}")
            count = self.client.count_laureates_by_motivation_keyword(request.keyword)
            return LaureateCountResponse(count=count, message="Success")
        except Exception as e:
            print(f"Error in CountLaureatesByMotivationKeyword: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetLaureateDetailsByName(self, request, context):
        try:
            print(f"Processing request for name: {request.firstname} {request.surname}")
            laureate_details = self.client.get_laureate_details_by_name(
                request.firstname, request.surname
            )
            details = [
                LaureateDetail(
                    year=detail['year'],
                    category=detail['category'],
                    motivation=detail['motivation']
                )
                for detail in laureate_details
            ]
            return LaureateDetailsResponse(
                details=details,
                message="Success" if laureate_details else "No prizes found"
            )
        except Exception as e:
            print(f"Error in GetLaureateDetailsByName: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

def serve(redis_host: str, redis_port: int, redis_password: str):
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
        ]
    )
    nobel_prize_pb2_grpc.add_NobelPrizeServiceServicer_to_server(
        NobelPrizeService(redis_host, redis_port, redis_password), 
        server
    )
    
    server_port = int(SERVER_PORT)
    server.add_insecure_port(f'[::]:{server_port}')
    server.start()
    print(f"Server started on port {server_port}")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    if not all([REDIS_HOST, REDIS_PORT, REDIS_PASSWORD]):
        print("Error: Missing required environment variables")
        exit(1)
    
    print(f"Starting server with Redis host: {REDIS_HOST}, port: {REDIS_PORT}")
    serve(
        redis_host=REDIS_HOST,
        redis_port=int(REDIS_PORT),
        redis_password=REDIS_PASSWORD
    )