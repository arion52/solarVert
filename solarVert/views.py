from django.http import JsonResponse, HttpResponse
from .models import PowerData
from .utils import get_weather_forecast, check_if_panel_defective, calculate_mppt
from .anomaly import ModelHandler
from django.conf import settings
import numpy as np
import json
import pickle
from django.views.decorators.http import require_http_methods
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

# Returns weather forecast suggestion
@api_view(['GET'])
@permission_classes([AllowAny])  # Allow unauthenticated access
def weather_advice(request):
    suggestion = get_weather_forecast()
    return JsonResponse({'suggestion': suggestion})

# Checks the status of a solar panel
@api_view(['GET'])
def check_panel_status(request, panel_id):
    panel_data = {
        'input_power': -1  # Simulated data
    }
    defective = check_if_panel_defective(panel_data)
    return JsonResponse({'panel_id': panel_id, 'defective': defective})

# Retrieves power data for a sensor
@api_view(['GET'])
def get_power_data(request, sensor_id):
    power_data = PowerData.objects.filter(sensor_id=sensor_id)
    response_data = [{
        'date': str(data.date),
        'input_power': data.input_power,
        'usage_power': data.usage_power
    } for data in power_data]
    return JsonResponse(response_data, safe=False)

# Default view for the app
def index(request):
    return HttpResponse("Welcome to the Solar Management App!")

# ANOMALY DETECTION MODEL
model_handler = ModelHandler(settings.ANOMALY_MODEL_PATH)

@require_http_methods(["POST", "GET"])
def predict_view(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'GET method received, but use POST instead'}, status=405)
    
    try:
        data = json.loads(request.body)
        input_data = data.get('input_data', None)

        if input_data is None:
            return JsonResponse({
                'status': 'error',
                'message': 'No input data provided'
            }, status=400)

        input_data = np.asarray(input_data)
        expected_shape = (1, 1, 22)
        if input_data.shape != expected_shape:
            return JsonResponse({
                'status': 'error',
                'message': f'Expected input shape {expected_shape}, but got {input_data.shape}'
            }, status=400)

        prediction = model_handler.predict(input_data)
        return JsonResponse({
            'input': input_data.tolist(),
            'prediction': prediction.tolist(),
            'status': 'success'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=400)

# GENERATION PREDICTION MODEL
try:
    with open('rfr.pkl', 'rb') as f:
        model = pickle.load(f)
except:
    print("Error loading model")
@require_http_methods(["POST"])
def predict_generated(request):
    try:
        data = json.loads(request.body)
        input_data = data.get('input_data', None)

        if input_data is None:
            return JsonResponse({
                'status': 'error',
                'message': 'No input data provided'
            }, status=400)

        input_data = np.asarray(input_data)
        if input_data.shape == (1, 7):
            input_data = input_data.reshape(1, 1, 7)
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Expected input shape (1, 7), but got {input_data.shape}'
            }, status=400)

        prediction = model.predict(input_data)
        return JsonResponse({
            'input': input_data.tolist(),
            'prediction': prediction.tolist(),
            'status': 'success'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=400)

# USAGE DETECTION MODEL
usage_model_handler = ModelHandler(settings.USAGE_MODEL_PATH)

@require_http_methods(["POST"])
def predict_usage(request):
    try:
        # Fetch the most recent data from the database for prediction
        # Assuming 'PowerData' stores the required fields for the model
        # You may need to adjust this based on your model requirements
        power_data = PowerData.objects.latest('date')  # Fetch the latest power data
        
        # Format data for the model, assuming your model expects a shape (1, 7)
        input_data = np.array([
            power_data.input_power, 
            power_data.usage_power,
            0,0,0,0,0
        ]).reshape(1, 7)  # Adjust based on the model's input requirements

        # Call the prediction model
        prediction = usage_model_handler.predict(input_data)

        return JsonResponse({
            'input': input_data.tolist(),
            'prediction': prediction.tolist(),
            'status': 'success'
        })

    except PowerData.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'No data available in the database'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
@api_view(['GET'])
def mppt_view(request):
    voltage = float(request.GET.get('voltage', 0))
    current = float(request.GET.get('current', 0))
    prev_voltage = float(request.GET.get('prev_voltage', 0))
    prev_current = float(request.GET.get('prev_current', 0))

    next_voltage, max_power = calculate_mppt(voltage, current, prev_voltage, prev_current)
    return JsonResponse({
        'next_voltage': next_voltage,
        'max_power': max_power
    })

@require_http_methods(["POST"])
def post_sensor_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            voltage = data.get('voltage')
            current = data.get('current')

            # Process or store the data as needed
            print(f"Received voltage: {voltage}, current: {current}")

            return JsonResponse({'status': 'success', 'message': 'Data received successfully'})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

from .models import PowerUsage

def predict_usage_from_db(request):
    # Fetch recent power usage data from the database
    latest_data = PowerUsage.objects.order_by('-dt').first()

    if latest_data:
        input_data = [
            latest_data.global_active_power,
            latest_data.global_reactive_power,
            latest_data.voltage,
            latest_data.global_intensity,
            latest_data.sub_metering_1,
            latest_data.sub_metering_2,
            latest_data.sub_metering_3,
        ]

        # Call the usage prediction model with the input data
        input_data = np.asarray(input_data).reshape(1, 1, 7)
        prediction = usage_model_handler.predict(input_data)

        return JsonResponse({
            'input': input_data.tolist(),
            'prediction': prediction.tolist(),
            'status': 'success'
        })

    return JsonResponse({'status': 'error', 'message': 'No data available'}, status=400)
