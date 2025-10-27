import json
import os
from datetime import datetime

# Load all repos (basic info)
with open('github_repos.json', 'r', encoding='utf-8') as f:
    all_repos = json.load(f)

# Load detailed repos
with open('github_repos_detailed.json', 'r', encoding='utf-8') as f:
    detailed_repos = json.load(f)

detailed_names = {r['name'] for r in detailed_repos}

# Output directory
output_dir = 'documents/github-projects'
os.makedirs(output_dir, exist_ok=True)

created_count = 0

for repo in all_repos:
    # Skip if already detailed
    if repo['name'] in detailed_names:
        continue
    
    # Create markdown filename
    filename = f"{output_dir}/{repo['name']}.md"
    
    # Build markdown content (basic info only)
    content = f"""# {repo['name']}

## プロジェクト概要

**リポジトリURL**: {repo['html_url']}  
**作成日**: {repo['created_at']}  
**最終更新**: {repo['updated_at']}  
**プライマリ言語**: {repo.get('language', 'N/A')}  
**プライベート**: {'はい' if repo.get('private', False) else 'いいえ'}  

### 説明
{repo.get('description', '説明なし')}

### 統計情報
- ⭐ Stars: {repo.get('stargazers_count', 0)}
- 🍴 Forks: {repo.get('forks_count', 0)}
- 👁️ Watchers: {repo.get('watchers_count', 0)}
- 🐛 Open Issues: {repo.get('open_issues_count', 0)}
- 📦 Size: {repo.get('size', 0)} KB

### プロジェクト設定
- デフォルトブランチ: {repo.get('default_branch', 'main')}
- アーカイブ済み: {'はい' if repo.get('archived', False) else 'いいえ'}
- Wiki有効: {'はい' if repo.get('has_wiki', False) else 'いいえ'}
- Issues有効: {'はい' if repo.get('has_issues', False) else 'いいえ'}
- Projects有効: {'はい' if repo.get('has_projects', False) else 'いいえ'}

"""

    # Add homepage if available
    if repo.get('homepage'):
        content += f"### ホームページ\n{repo['homepage']}\n\n"

    # Add clone URLs
    content += f"""### クローンURL
- HTTPS: `{repo.get('clone_url')}`
- SSH: `{repo.get('ssh_url')}`

### 補足
詳細情報は直接リポジトリを参照してください: {repo['html_url']}

---
*ドキュメント生成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*注: このドキュメントは基本情報のみを含みます（README取得エラーのため）*
"""

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {filename}")
    created_count += 1

print(f"\n作成完了: {created_count}個のドキュメント")
