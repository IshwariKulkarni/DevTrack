from django.shortcuts import render
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import json
# Create your views here.
REPORTERS_FILE_PATH = 'reporters.json'
ISSUES_FILE_PATH = 'issues.json'    

##helper functions
def load_reporters():
    if not os.path.exists(REPORTERS_FILE_PATH):
        return []
    with open(REPORTERS_FILE_PATH, 'r') as file:
        try:
            return json.loads(file.read())
        except json.JSONDecodeError:
            return []

def save_reporters(reporters):
    with open(REPORTERS_FILE_PATH, 'w') as file:
        json.dump(reporters, file, indent=2)

##functions
def create_reporters(request):
    data = request.data
    try:
        reporter = Reporter(
            id=data.get('id'),
            name=data.get('name'), 
            email=data.get('email'),
            team=data.get('team')
        )
        reporter.validate()
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    reporters = load_reporters()
    reporters.append(reporter.to_dict())
    save_reporters(reporters)

    return Response({'message': 'Reporter created successfully'}, status=status.HTTP_201_CREATED)

def get_all_reporters():
    reporters = load_reporters()
    return Response(reporters, status=status.HTTP_200_OK)

def get_reporter_by_id(reporter_id):
    # Ensure reporter_id is an int for comparison
    try:
        reporter_id = int(reporter_id)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid reporter id'}, status=status.HTTP_400_BAD_REQUEST)

    reporters = load_reporters()
    for reporter in reporters:
        try:
            if int(reporter.get('id')) == reporter_id:
                return Response(reporter, status=status.HTTP_200_OK)
        except (TypeError, ValueError):
            # skip reporters with non-integer ids
            continue
    return Response({'error': 'Reporter not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
def reporters(request):
    if request.method == 'GET':
        query_id = request.query_params.get('id')
        if query_id is not None:
            return get_reporter_by_id(query_id)
        return get_all_reporters()
    elif request.method == 'POST':
        return create_reporters(request)