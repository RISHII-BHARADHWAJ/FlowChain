from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def forecast_dashboard(request):
    from forecasting.models import DemandForecast
    forecasts = DemandForecast.objects.select_related('product').order_by('-forecast_date')[:15]
    return render(request, 'forecasting/forecast_dashboard.html', {
        'forecasts': forecasts
    })
