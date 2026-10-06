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
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        try:
            return json.loads(file.read())
        except json.JSONDecodeError:
            return []

def save_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

##functions
def create_reporters(request):
    data = request.data
    reporters = load_data(REPORTERS_FILE_PATH)
    try:
        reporter = Reporter(
            id=len(reporters) + 1,
            name=data.get('name'), 
            email=data.get('email'),
            team=data.get('team')
        )
        reporter.validate()
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    reporters.append(reporter.to_dict())
    save_data(reporters, REPORTERS_FILE_PATH)

    return Response({'message': 'Reporter created successfully'}, status=status.HTTP_201_CREATED)

def get_all_reporters():
    reporters = load_data(REPORTERS_FILE_PATH)
    return Response(reporters, status=status.HTTP_200_OK)

def get_reporter_by_id(reporter_id):
    # Ensure reporter_id is an int for comparison
    try:
        reporter_id = int(reporter_id)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid reporter id'}, status=status.HTTP_400_BAD_REQUEST)

    reporters = load_data(REPORTERS_FILE_PATH)
    for reporter in reporters:
        try:
            if int(reporter.get('id')) == reporter_id:
                return Response(reporter, status=status.HTTP_200_OK)
        except (TypeError, ValueError):
            # skip reporters with non-integer ids
            continue
    return Response({'error': 'Reporter not found'}, status=status.HTTP_404_NOT_FOUND)


##issues functions

def create_issues(request):
    data = request.data
    priority = data.get('priority')
    issues = load_data(ISSUES_FILE_PATH)
    try:
        if priority == 'critical':
            issue = CriticalIssue(
                id=len(issues) + 1,
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=priority,
                reporter_id=data.get('reporter_id'),
                created_at=data.get('created_at')
            )
        elif priority == 'low':
            issue = LowPriorityIssue(
                id=len(issues) + 1,
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=priority,
                reporter_id=data.get('reporter_id'),
                created_at=data.get('created_at')
            )
        else:
            issue = Issue(
                id=len(issues) + 1,
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=priority,
                reporter_id=data.get('reporter_id'),
                created_at=data.get('created_at')
            )
        issue.validate()
    
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #save to issues.json
    
    issues.append(issue.to_dict())
    save_data(issues, ISSUES_FILE_PATH)

    #return the response with correct issue description based on the issue type
    response_data = issue.to_dict()
    response_data['message'] = issue.describe()  # Add the description to the response

    return Response(response_data, status=status.HTTP_201_CREATED)

#get all issues
def get_all_issues():
    issues = load_data(ISSUES_FILE_PATH)
    return Response(issues, status=status.HTTP_200_OK)

#get issue by id
def get_issue_by_id(issue_id):
    try:
        issue_id = int(issue_id)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid issue id'}, status=status.HTTP_400_BAD_REQUEST)
    issues = load_data(ISSUES_FILE_PATH)
    for issue in issues:
        if int(issue.get('id')) == int(issue_id):
            return Response(issue, status=status.HTTP_200_OK)
    return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

#get issue by status
def get_issue_by_status(status_name):
    issues = load_data(ISSUES_FILE_PATH)
    filtered_issues = [issue for issue in issues if issue.get('status') == status_name]
    return Response(filtered_issues, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def reporters(request):
    if request.method == 'GET':
        query_id = request.query_params.get('id')
        if query_id is not None:
            return get_reporter_by_id(query_id)
        return get_all_reporters()
    elif request.method == 'POST':
        return create_reporters(request)
    
@api_view(['GET', 'POST'])
def issues(request):
    if request.method == 'GET':
        query_id = request.query_params.get('id')
        query_status = request.query_params.get('status')
        if query_id is not None:
            return get_issue_by_id(query_id)
        elif query_status is not None:
            return get_issue_by_status(query_status)
        return get_all_issues()
    elif request.method == 'POST':
        return create_issues(request)