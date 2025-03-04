import json
from screen_grant import make_screen_grant_prompt
from utils import extract_xml_tag, clean_xml_string
import asyncio
import aiohttp
from call_claude_3_7 import call_claude_3_7
from typing import Dict, Any, List


async def screen_project(session, project: Dict[Any, Any]) -> Dict[Any, Any]:
    """Screen a single project and return the results."""
    # Convert the project dictionary to a string representation or extract the description
    project_description = project.get("description", "")
    if not isinstance(project_description, str):
        project_description = json.dumps(project)
        
    prompt = make_screen_grant_prompt(project_description)
    
    # You'll need to replace this with your actual API call
    # This is a placeholder for the API call to your LLM
    response = await call_claude_3_7(prompt)
    response_text = response.content[0].text
    
    # Parse the XML tags from the response
    score = extract_xml_tag(clean_xml_string(response_text), "promise_score")
    
    # Add the original project ID and title to the results
    result = {
        "project_id": project.get("id"),
        "project_title": project.get("title"),
        "score": score,
        "model_output": response_text,
    }
    
    return result


async def screen_all_projects() -> List[Dict[Any, Any]]:
    """Screen all projects in the manifund_projects.json file."""
    # Load the projects from the JSON file
    with open("manifund_projects.json", "r") as f:
        projects = json.load(f)
        projects = projects
    
    results = []
    
    # Create a session for making API calls
    async with aiohttp.ClientSession() as session:
        # Create tasks for screening each project
        tasks = [screen_project(session, project) for project in projects]
        
        # Set maximum concurrency to 10
        semaphore = asyncio.Semaphore(10)
        
        async def bounded_screen_project(project):
            async with semaphore:
                return await screen_project(session, project)
        
        # Create tasks with bounded concurrency
        tasks = [bounded_screen_project(project) for project in projects]
        
        # Execute tasks concurrently
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            print(f"Screened project {i+1}/{len(projects)}: "
                  f"{result['project_title']}")
    
    return results


def save_results(
    results: List[Dict[Any, Any]], 
    output_file: str = "screening_results.json"
):
    """Save the screening results to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_file}")


async def main():
    with open('manifund_projects.json') as f:
        project_count = len(json.load(f))
    print(f"Starting to screen {project_count} projects...")
    
    results = await screen_all_projects()
    
    save_results(results)
    
    print(f"Screened {len(results)} projects")


if __name__ == "__main__":
    asyncio.run(main())
