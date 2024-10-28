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
            count = self.client.count_laureates_by_motivation_keyword(
                request.keyword)
            return LaureateCountResponse(count=count, message="Success")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetLaureateDetailsByName(self, request, context):
        """
        Implement Query 3: Get laureate details by name
        """
        try:
            laureate_details = self.client.get_laureate_details_by_name(
                request.firstname, request.surname)
            details = [
                LaureateDetail(year=detail['year'], category=detail['category'],
                                motivation=detail['motivation'])
                for detail in laureate_details
            ]
            return LaureateDetailsResponse(details=details, message=("Success" 
                                    if laureate_details else "No prizes found"))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
