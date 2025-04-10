import os
import requests
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

N8NHACKERS_API_KEY = os.getenv("N8NHACKERS_API_KEY")
N8NHACKERS_API_URL = os.getenv("N8NHACKERS_API_URL")

# Dynamically load instances from environment variables
INSTANCES = []
for i in range(1, 11):  # Assuming up to 10 instances
    instance_name = os.getenv(f"INSTANCE_NAME{i}")
    instance_url = os.getenv(f"INSTANCE_URL{i}")
    instance_api_key = os.getenv(f"INSTANCE_API_KEY{i}")
    if instance_name and instance_url and instance_api_key:
        INSTANCES.append((instance_name, instance_url, instance_api_key))
        
def get_executions_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        final_url = f'{instance_url}/api/v1/executions?limit=1000'
        response = requests.get(final_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching executions from {instance_url}: {e}")
        return None

def get_workflows_from_n8n(instance_url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        final_url = f'{instance_url}/api/v1/workflows?limit=1000'
        response = requests.get(final_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching executions from {instance_url}: {e}")
        return None

def check_up(instance_url, api_key):
    #check if instance_url is up
    try:
        response = requests.get(instance_url)
        return response.ok
    except Exception as e:
        return False
    
def check_access(instance_url, api_key):
    headers = {
        'content-type': 'application/json',
        'X-N8N-API-KEY': api_key
    }
    final_url = f'{instance_url}/api/v1/executions?limit=1'
    options = {
        'method': 'GET',
        'url': final_url,
        'headers': headers
    }
    options['agentOptions'] = {
        'rejectUnauthorized': False
    }
    response = requests.get(options['url'], headers=options['headers'])
    return response.status_code < 400
    

def push_data_to_n8nhackers(instance_name, type, raw):
    data = {
        'instance_name': instance_name,
        'type': type,
        'raw': raw
    }
    
    headers = {
        'X-API-KEY': N8NHACKERS_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(f'{N8NHACKERS_API_URL}/api/v1/agent/data', json=data, headers=headers)
        response.raise_for_status()
        print(f"Data pushed successfully for {instance_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error pushing data for {instance_name}: {e}")
    
    
# Function that fetches data from each n8n instance and pushes it to the API
def do_task(type):
    for instance_name, instance_url, instance_api_key in INSTANCES:
        print(f"Fetching data from {instance_name}...")
        if check_up(instance_url, instance_api_key):
            if check_access(instance_url, instance_api_key):
                if type == 'alarms':
                    data = get_executions_from_n8n(instance_url, instance_api_key)
                elif type == 'backups':
                    data = get_workflows_from_n8n(instance_url, instance_api_key)
                else:
                    print(f"Unknown type: {type}")
                    return
                    
                if data:
                    push_data_to_n8nhackers(instance_name, type, data)
            else:
                print(f"Access denied for {instance_name}")
        else:
            print(f"{instance_name} is down")
   

# Schedule the task every x minutes (e.g., every 10 minutes)
print("Scheduling task to run every 1 minute...")
# schedule.every(5).minutes.do(lambda: do_task('alarms'))
# schedule.every(1).day.at("06:00").do(lambda: do_task('backups'))

do_task('alarms')  # Run immediately for testing

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)  # Check every second for any scheduled tasks
