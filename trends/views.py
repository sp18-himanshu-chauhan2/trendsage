from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import TrendQuery, TrendResult
from .serializers import TrendQuerySerializer, TrendResultSerializer, TrendQueryCreateSerializer
from .tasks import process_trend_query
# Create your views here.


class TrendListView(APIView):
    def get(self, request):
        industry = request.query_params.get('industry')
        region = request.query_params.get('region')
        persona = request.query_params.get('persona')
        date_range = request.query_params.get('date_range')

        if not all([industry, region, persona, date_range]):
            return Response(
                {
                    'error': 'All parameters (industry, region, persona, date_range) are required.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = (
            TrendQuery.objects.filter(
                industry=industry,
                region=region,
                persona=persona,
                date_range=date_range,
                status='completed',
            ).order_by('-created_at').first()
        )

        if not query:
            return Response([], status=status.HTTP_200_OK)

        results = TrendResult.objects.filter(
            query=query).order_by('final_score')
        serializer = TrendResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrendQueryDetailView(APIView):
    def get(self, request, id):
        query = get_object_or_404(TrendQuery, id=id)
        serializer = TrendQuerySerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrendQueryCreateView(APIView):
    def post(self, request):
        serializer = TrendQueryCreateSerializer(data=request.data)

        if serializer.is_valid():
            query = serializer.save(status='pending')
            process_trend_query.delay(str(query.id))
            return Response(
                {
                    'message': 'Trend query created successfully. Processing started.',
                    'query_id': str(query.id),
                    'status': query.status,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
