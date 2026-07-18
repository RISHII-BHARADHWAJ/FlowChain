"""Analytics, Forecasting, Reports, Notifications ViewSets"""
# ── FORECASTING ───────────────────────────────────────────────────────────────
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class DemandForecastViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse', 'period_type']
    ordering = ['-forecast_date']

    def get_queryset(self):
        from forecasting.models import DemandForecast
        return DemandForecast.objects.select_related('product', 'warehouse').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from forecasting.serializers import DemandForecastSerializer
        return DemandForecastSerializer


class StockForecastSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse', 'stockout_risk']
    ordering = ['snapshot_date']

    def get_queryset(self):
        from forecasting.models import StockForecastSnapshot
        return StockForecastSnapshot.objects.select_related('product', 'warehouse').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from forecasting.serializers import StockForecastSnapshotSerializer
        return StockForecastSnapshotSerializer
