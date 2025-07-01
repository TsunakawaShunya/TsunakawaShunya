import os
import requests
import base64
import json
import re

def get_github_api_headers():
    token = os.environ.get('PERSONAL_ACCESS_TOKEN')
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

def get_repositories():
    headers = get_github_api_headers()
    repositories = []
    
    # Get user's repositories
    user_repos_url = 'https://api.github.com/user/repos'
    user_repos_response = requests.get(user_repos_url, headers=headers, params={'type': 'all', 'per_page': 100})
    
    if user_repos_response.status_code == 200:
        repositories.extend(user_repos_response.json())
    else:
        print(f"Error fetching user repositories: {user_repos_response.status_code}")
        print(user_repos_response.text)
    
    # Get C-FO organization repositories
    org_repos_url = 'https://api.github.com/orgs/C-FO/repos'
    org_repos_response = requests.get(org_repos_url, headers=headers, params={'per_page': 100})
    
    if org_repos_response.status_code == 200:
        repositories.extend(org_repos_response.json())
    else:
        print(f"Error fetching organization repositories: {org_repos_response.status_code}")
        print(org_repos_response.text)
    
    return repositories

def get_repository_languages(repo):
    headers = get_github_api_headers()
    languages_url = repo['languages_url']
    languages_response = requests.get(languages_url, headers=headers)
    return languages_response.json()

def aggregate_languages(repositories):
    language_totals = {}
    
    for repo in repositories:
        languages = get_repository_languages(repo)
        for lang, bytes_count in languages.items():
            if lang not in language_totals:
                language_totals[lang] = 0
            language_totals[lang] += bytes_count
    
    total_bytes = sum(language_totals.values())
    language_percentages = {
        lang: round((bytes / total_bytes) * 100, 2) 
        for lang, bytes in language_totals.items()
    }
    
    return sorted(language_percentages.items(), key=lambda x: x[1], reverse=True)

def generate_language_stats_markdown(language_stats):
    markdown = "### Languages and Tools Usage\n\n"
    markdown += "| Language | Percentage |\n"
    markdown += "|----------|------------|\n"
    
    for lang, percentage in language_stats:
        markdown += f"| {lang} | {percentage}% |\n"
    
    return markdown

def update_readme(language_stats_markdown):
    with open('README.md', 'r') as f:
        readme_content = f.read()
    
    # Replace or insert language stats section
    language_stats_pattern = r'(### Languages and Tools Usage\n\n\|.*\|\n\|.*\|\n).*'
    if re.search(language_stats_pattern, readme_content, re.DOTALL):
        readme_content = re.sub(
            language_stats_pattern, 
            language_stats_markdown, 
            readme_content, 
            flags=re.DOTALL
        )
    else:
        # If section doesn't exist, append to the end
        readme_content += "\n\n" + language_stats_markdown
    
    with open('README.md', 'w') as f:
        f.write(readme_content)

def generate_github_stats_urls(repositories):
    headers = get_github_api_headers()
    
    # Count total commits for personal and org repositories
    total_commits = 0
    for repo in repositories:
        commits_url = f"{repo['url']}/commits"
        commits_response = requests.get(commits_url, headers=headers)
        total_commits += len(commits_response.json())
    
    # Generate URLs with updated commit information
    top_langs_url = f"https://github-readme-stats.vercel.app/api/top-langs?username=tsunakawashunya&show_icons=true&locale=en&layout=compact&count_private=true"
    github_stats_url = f"https://github-readme-stats.vercel.app/api?username=tsunakawashunya&show_icons=true&locale=en&count_private=true"
    github_streak_url = f"https://github-readme-streak-stats.herokuapp.com/?user=tsunakawashunya&total_commits={total_commits}"
    
    return top_langs_url, github_stats_url, github_streak_url

def update_readme_stats_urls(top_langs_url, github_stats_url, github_streak_url):
    with open('README.md', 'r') as f:
        readme_content = f.read()
    
    # Replace URLs for top languages, github stats, and streak stats
    readme_content = re.sub(
        r'<img align="left" src="https://github-readme-stats\.vercel\.app/api/top-langs\?.*?" alt="tsunakawashunya" />',
        f'<img align="left" src="{top_langs_url}" alt="tsunakawashunya" />',
        readme_content
    )
    
    readme_content = re.sub(
        r'<img align="center" src="https://github-readme-stats\.vercel\.app/api\?.*?" alt="tsunakawashunya" />',
        f'<img align="center" src="{github_stats_url}" alt="tsunakawashunya" />',
        readme_content
    )
    
    readme_content = re.sub(
        r'<img align="center" src="https://github-readme-streak-stats\.herokuapp\.com/\?.*?" alt="tsunakawashunya" />',
        f'<img align="center" src="{github_streak_url}" alt="tsunakawashunya" />',
        readme_content
    )
    
    with open('README.md', 'w') as f:
        f.write(readme_content)

def main():
    repositories = get_repositories()
    language_stats = aggregate_languages(repositories)
    language_stats_markdown = generate_language_stats_markdown(language_stats)
    update_readme(language_stats_markdown)
    
    top_langs_url, github_stats_url, github_streak_url = generate_github_stats_urls(repositories)
    update_readme_stats_urls(top_langs_url, github_stats_url, github_streak_url)

if __name__ == '__main__':
    main()
