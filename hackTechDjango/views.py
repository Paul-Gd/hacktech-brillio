from django.http import HttpResponse
from django.http import JsonResponse

def index(request):
    return HttpResponse("hi")

# TODO: replace this with django rest framework where we group Models and inputs
def predict_data(request):
    # Example data to return
    data = {
        'message': 'Hello, world!',
        'status': 'success'
    }
    return JsonResponse(data)
