import os
import requests
import schedule
import time
from dotenv import load_dotenv
import gzip
import json as json_lib
from io import BytesIO

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
        
def get_executions_from_n8n(instance_url, api_key, status=None, include_data=False, paginate=False, cursor=None):
    headers = {
        'accept': 'application/json',
        'X-N8N-API-KEY': api_key
    }
    
    options = {
        'method': 'GET',
        'url': f'{instance_url}/api/v1/executions?limit=100',
        'headers': headers
    }
    
    if status is not None and status != '':
        options['url'] = f'{options["url"]}&status={status}'
    
    if include_data:
        options['url'] = f'{options["url"]}&includeData=true'
        
    if cursor:
        options['url'] = f'{options["url"]}&cursor={cursor}'
    
    print(options['url'])
    
    options['agentOptions'] = {
        'rejectUnauthorized': False
    }
    
    response = requests.get(options['url'], headers=options['headers'])
    print (f"Response: {response.status_code}")
    if response.status_code != 200:
        print (f"Error fetching executions from {instance_url}: {response.status_code}")
        return []
    else:
        try:
            obj = response.json()
            
            final_executions = list(obj['data'])
            
            print(f"Fetched {len(final_executions)} executions from {instance_url}")
            
            if paginate and 'nextCursor' in obj and obj['nextCursor'] is not None:
                final_executions += get_executions_from_n8n(instance_url, api_key, status, include_data, paginate, obj['nextCursor'])
        
            return final_executions
        except Exception as e:
            print(f"Error processing executions from {instance_url}: {e}")
            return []

def get_workflows_from_n8n(instance_url, api_key, cursor=None):
    headers = {
        'content-type': 'application/json',
        'X-N8N-API-KEY': api_key
    }
    options = {
        'method': 'GET',
        'url': f'{instance_url}/api/v1/workflows?limit=250',
        'headers': headers
    }
    options['agentOptions'] = {
        'rejectUnauthorized': False
    }
    
    if cursor:
        options['url'] = f'{options["url"]}&cursor={cursor}'
    
    response = requests.get(options['url'], headers=options['headers'])
    if response.status_code != 200:
        print (f"Error fetching workflows from {instance_url}: {response.status_code}")
        return []
    else:
        try:
            obj = response.json()
            final_workflows = obj['data']
            if 'nextCursor' in obj and obj['nextCursor'] is not None:
                final_workflows += get_workflows_from_n8n(instance_url, api_key, obj['nextCursor'])
                
            return final_workflows
        except Exception as e:
            print(f"Error fetching workflows from {instance_url}: {e}")
            return []

def check_up(instance_url, api_key):
    #check if instance_url is up
    try:
        response = requests.get(instance_url)
        return response.ok
    except Exception as e:
        return False
    
def check_access(instance_url, api_key):
    headers = {
        'accept': 'application/json',
        'x-n8n-api-key': api_key
    }
    options = {
        'method': 'GET',
        'url': f'{instance_url}/api/v1/workflows?limit=1',
        'headers': headers
    }
    options['agentOptions'] = {
        'rejectUnauthorized': False
    }
        
    # print (f"Headers: {options['headers']}")
    response = requests.get(options['url'], headers=options['headers'])
    print (f"Response: {response.status_code}")
    return response.status_code == 200

def push_data_to_n8nhackers(instance_name, type, data):
    json = {
        'instance_name': instance_name,
        'type': type,
        'data': data
    }
    print(f"Pushing data to n8nhackers for {instance_name}...")
    
    # Compress data with gzip
    compressed_data = BytesIO()
    with gzip.GzipFile(fileobj=compressed_data, mode='wb') as gz_file:
        gz_file.write(json_lib.dumps(json).encode('utf-8'))
    compressed_data.seek(0)
    
    headers = {
        'X-API-KEY': N8NHACKERS_API_KEY,
        'Content-Type': 'application/json',
        'Content-Encoding': 'gzip'
    }
    try:
        response = requests.post(f'{N8NHACKERS_API_URL}/api/v1/agent/data', data=compressed_data.read(), headers=headers)
        response.raise_for_status()
        print(f"Data pushed successfully for {instance_name}")
    except requests.exceptions.RequestException as e:
        output = e.response.json() if e.response else str(e)
        print(f"Error pushing data for {instance_name}: {response.status_code if e.response else 'N/A'} {output}")
    
# Function that fetches data from each n8n instance and pushes it to the API
def do_task(type):
    for instance_name, instance_url, instance_api_key in INSTANCES:
        print(f"Fetching data from {instance_name}...")
        if check_up(instance_url, instance_api_key):
            print (f"{instance_name} is up")
            if check_access(instance_url, instance_api_key):
                print(f"Access granted for {instance_name}")
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
print("Scheduling tasks ...")
# schedule.every(1).minutes.do(lambda: do_task('alarms'))
# schedule.every(1).day.at("06:00").do(lambda: do_task('backups'))

do_task('alarms')  # Run immediately for testing

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)  # Check every second for any scheduled tasks
