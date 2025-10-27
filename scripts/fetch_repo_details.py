import json
import requests
import time

# Load basic repo data
with open('github_repos.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

detailed_repos = []

for i, repo in enumerate(repos):
    print(f"Fetching {i+1}/{len(repos)}: {repo['name']}")
    
    # Get detailed repo info
    try:
        response = requests.get(repo['url'], headers={'Accept': 'application/vnd.github+json'})
        if response.status_code == 200:
            detailed_repo = response.json()
            
            # Get README if exists
            readme_url = f"https://api.github.com/repos/Tenormusica2024/{repo['name']}/readme"
            readme_response = requests.get(readme_url, headers={'Accept': 'application/vnd.github.raw'})
            if readme_response.status_code == 200:
                detailed_repo['readme_content'] = readme_response.text
            else:
                detailed_repo['readme_content'] = None
            
            # Get topics
            topics_url = f"https://api.github.com/repos/Tenormusica2024/{repo['name']}/topics"
            topics_response = requests.get(topics_url, headers={'Accept': 'application/vnd.github.mercy-preview+json'})
            if topics_response.status_code == 200:
                detailed_repo['topics'] = topics_response.json().get('names', [])
            else:
                detailed_repo['topics'] = []
            
            detailed_repos.append(detailed_repo)
            time.sleep(0.5)  # Rate limiting
        else:
            print(f"  Error: {response.status_code}")
    except Exception as e:
        print(f"  Exception: {e}")

# Save detailed data
with open('github_repos_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_repos, f, indent=2, ensure_ascii=False)

print(f"\nTotal detailed repos saved: {len(detailed_repos)}")
