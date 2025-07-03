import requests
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  
from django.contrib.auth import logout

def loginpage(request):
    return render(request, 'loginpage.html')

def login(request):
    if request.method == 'POST':
        # You can optionally capture username & password
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 🚀 Direct redirect to admin dashboard without authentication
        return redirect('admindashboard')  # Replace with your actual URL name
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def admindashboard(request):
    return render(request, 'admindashboard.html')

def analytics(request):
    view_mode = request.GET.get('groupBy', 'week')
    current_date_str = request.GET.get('date', None)
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)

    base_url = 'https://api-fxz7qcfy4q-uc.a.run.app/api/analytics'
    params = {'groupBy': view_mode}

    if view_mode in ['day', 'week'] and current_date_str:
        params['date'] = current_date_str
    elif view_mode == 'month' and year and month:
        params['year'] = year
        params['month'] = month

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)  # ✅ FIXED: Wrap in JsonResponse
        else:
            return JsonResponse(
                {'error': f"Failed to load data: {response.status_code}"},
                status=response.status_code
            )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

    

    