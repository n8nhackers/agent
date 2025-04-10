import os
import requests
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
INSTANCES = os.getenv("INSTANCES")

print (INSTANCES)

def get_executions_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/api/v1/executions?limit=1000', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching executions from {instance_url}: {e}")
        return None
    
def get_workflows_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/api/v1/workflows?limit=1000', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflows from {instance_url}: {e}")
        return None
    
def get_audit_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.post(f'{instance_url}/api/v1/audit', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching audit data from {instance_url}: {e}")
        return None
    
def get_users_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/api/v1/users?limit=1000', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users from {instance_url}: {e}")
        return None
    
def get_projects_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/api/v1/projects?limit=1000', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects from {instance_url}: {e}")
        return None

def get_tags_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/api/v1/tags?limit=1000', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tags from {instance_url}: {e}")
        return None

# Function to get data from n8n instance
def get_data_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(f'{instance_url}/your-api-endpoint', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {instance_url}: {e}")
        return None

# Function to push data to api.n8nhackers.com
def push_data_to_api(data):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    try:
        response = requests.post('https://api-dev.n8nhackers.com/your-api-endpoint', json=data, headers=headers)
        response.raise_for_status()
        print("Data pushed successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error pushing data to API: {e}")

# Function that fetches data from each n8n instance and pushes it to the API
def task():
    for instance in INSTANCES:
        instance_name, instance_url, instance_api_key = instance.split(',')
        print(f"Fetching data from {instance_name}...")
        # data = get_data_from_n8n(instance_url, instance_api_key)
        # if data:
        #     push_data_to_api(data)

# Schedule the task every x minutes (e.g., every 10 minutes)
print ("Scheduling task to run every 1 minute...")
schedule.every(1).minutes.do(task)

task()

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)  # Check every second for any scheduled tasks
