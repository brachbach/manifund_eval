import requests
import json
from datetime import datetime
import time

def fetch_all_projects():
    """
    Fetches all projects from the Manifund API by paginating through all pages
    and returns them as a list.
    """
    base_url = "https://manifund.org/api/v0/projects"
    all_projects = []
    
    # Start with the first page (no before parameter)
    current_url = base_url
    
    while True:
        print(f"Fetching: {current_url}")
        
        # Make the API request
        response = requests.get(current_url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            break
        
        # Parse the JSON response
        projects = response.json()
        
        # If we received no projects, we've reached the end
        if not projects:
            print("No more projects found. Finished fetching.")
            break
        
        # Add the projects to our list
        all_projects.extend(projects)
        print(f"Fetched {len(projects)} projects. Total so far: {len(all_projects)}")
        
        # Get the timestamp of the oldest project in this batch for pagination
        oldest_timestamp = min(project["created_at"] for project in projects)
        
        # Set up the URL for the next page
        current_url = f"{base_url}?before={oldest_timestamp}"
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    return all_projects

def save_to_json(projects, filename="manifund_projects.json"):
    """
    Saves the list of projects to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(projects)} projects to {filename}")

if __name__ == "__main__":
    print(f"Starting data collection at {datetime.now().isoformat()}")
    all_projects = fetch_all_projects()
    save_to_json(all_projects)
    print(f"Completed at {datetime.now().isoformat()}")
    print(f"Total projects collected: {len(all_projects)}")
