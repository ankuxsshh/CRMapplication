import requests
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
import json

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

def logout(request):
    return redirect('loginpage')  # Redirect to login page after logout

def admindashboard(request):
    base_url = 'https://api-fxz7qcfy4q-uc.a.run.app/api/analytics'
    current_year = datetime.now().year
    current_month = datetime.now().month

    try:
        params = {
            'groupBy': 'month',
            'year': current_year,
            'month': current_month
        }
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            month_data = response.json()
            total_count = month_data.get("totalCount", 0)
            week_ranges = [entry.get("weekRange", "") for entry in month_data.get("data", [])]
            week_counts = [entry.get("count", 0) for entry in month_data.get("data", [])]
        else:
            total_count = 0
            week_ranges = []
            week_counts = []

    except Exception as e:
        total_count = 0
        week_ranges = []
        week_counts = []

    # 🔽 Fetch total number of properties
    try:
        prop_response = requests.get('https://api-fxz7qcfy4q-uc.a.run.app/getProperties', timeout=10)
        prop_response.raise_for_status()
        properties_data = prop_response.json()
        total_properties = len(properties_data) if isinstance(properties_data, list) else 0
    except Exception as e:
        total_properties = 0

    return render(request, 'admindashboard.html', {
        'month': datetime.now().strftime('%B'),
        'total_count': total_count,
        'week_ranges': week_ranges,
        'week_counts': week_counts,
        'total_properties': total_properties,  # ✅ pass to template
    })

def analytics(request):
    year = request.GET.get('year', '2025')
    base_url = 'https://api-fxz7qcfy4q-uc.a.run.app/api/analytics'
    all_months_data = []

    try:
        for month in range(1, 13):
            params = {'groupBy': 'month', 'year': year, 'month': month}
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                month_data = response.json()
                all_months_data.append({
                    'month': month,
                    'data': month_data
                })
            else:
                all_months_data.append({
                    'month': month,
                    'data': {'totalCount': 0}
                })

        return render(request, 'analytics.html', {
            'year': year,
            'analytics': all_months_data
        })

    except Exception as e:
        return render(request, 'analytics.html', {
            'year': year,
            'analytics': [],
            'error': str(e)
        })


def properties(request):
    """Fetch and display all properties"""
    try:
        response = requests.get('https://api-fxz7qcfy4q-uc.a.run.app/getProperties', timeout=10)
        response.raise_for_status()
        properties_data = response.json()
        
        # Ensure we always get a list even if API returns something else
        if not isinstance(properties_data, list):
            properties_data = []
            
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        properties_data = []
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        properties_data = []
    
    return render(request, 'properties.html', {'properties': properties_data})

@csrf_exempt
def delete_property(request, property_id):
    """Handle property deletion by ID"""
    if request.method != 'DELETE':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method',
            'message': 'Only DELETE requests are allowed'
        }, status=405)

    try:
        # Validate property_id
        if not property_id or not isinstance(property_id, str):
            return JsonResponse({
                'success': False,
                'error': 'Invalid property ID',
                'message': 'A valid property ID is required'
            }, status=400)

        # Call external API
        api_url = f"https://api-fxz7qcfy4q-uc.a.run.app/deleteproperty/{property_id}"
        response = requests.delete(api_url, timeout=10)
        response.raise_for_status()

        return JsonResponse({
            'success': True,
            'message': 'Property deleted successfully',
            'property_id': property_id
        })

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred: {str(http_err)}"
        if hasattr(http_err, 'response') and http_err.response:
            error_msg += f" - {http_err.response.text}"
        return JsonResponse({
            'success': False,
            'error': 'api_error',
            'message': error_msg
        }, status=http_err.response.status_code if hasattr(http_err, 'response') else 500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'server_error',
            'message': f"An error occurred: {str(e)}"
        }, status=500)

@csrf_exempt
def update_property(request):
    """Handle property updates"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'invalid_method',
            'message': 'Only POST requests are allowed'
        }, status=405)

    try:
        # Parse and validate request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'invalid_json',
                'message': 'Invalid JSON data received'
            }, status=400)

        # Required fields validation
        required_fields = ['id', 'name', 'location', 'price']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': 'missing_fields',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Prepare API payload
        payload = {
            "propertyId": data['id'],
            "name": data['name'],
            "location": data['location'],
            "type": data.get('type', ''),
            "subtype": data.get('subtype', ''),
            "bhk": data.get('bhk', 0),
            "price": data['price'],
            "sqft": data.get('sqft', 0),
            "propertyDescription": data.get('description', ''),
            "plotArea": data.get('plotArea', ''),
            "unit": data.get('unit', ''),
            "verified": data.get('verified', False),
            "imageUrls": data.get('images', [])
        }

        # Call external API
        api_url = "https://api-fxz7qcfy4q-uc.a.run.app/upload"
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()

        return JsonResponse({
            'success': True,
            'message': 'Property updated successfully',
            'property_id': data['id']
        })

    except requests.exceptions.RequestException as req_err:
        error_msg = f"API request failed: {str(req_err)}"
        if hasattr(req_err, 'response') and req_err.response:
            error_msg += f" - {req_err.response.text}"
        return JsonResponse({
            'success': False,
            'error': 'api_error',
            'message': error_msg
        }, status=req_err.response.status_code if hasattr(req_err, 'response') else 500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'server_error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500)