import json
import os
from datetime import datetime

# Load detailed repo data
with open('github_repos_detailed.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

# Create github-projects directory in documents
output_dir = 'documents/github-projects'
os.makedirs(output_dir, exist_ok=True)

for repo in repos:
    # Create markdown filename
    filename = f"{output_dir}/{repo['name']}.md"
    
    # Build markdown content
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

    # Add topics if available
    if repo.get('topics'):
        content += "### トピック\n"
        for topic in repo['topics']:
            content += f"- {topic}\n"
        content += "\n"

    # Add homepage if available
    if repo.get('homepage'):
        content += f"### ホームページ\n{repo['homepage']}\n\n"

    # Add README content if available
    if repo.get('readme_content'):
        content += "## README\n\n"
        content += "```\n"
        content += repo['readme_content'][:5000]  # Limit to 5000 chars
        if len(repo['readme_content']) > 5000:
            content += "\n...(省略)...\n"
        content += "\n```\n\n"

    # Add license info if available
    if repo.get('license'):
        content += f"### ライセンス\n{repo['license'].get('name', 'N/A')}\n\n"

    # Add clone URLs
    content += f"""### クローンURL
- HTTPS: `{repo.get('clone_url')}`
- SSH: `{repo.get('ssh_url')}`

---
*ドキュメント生成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {filename}")

print(f"\n✅ 全{len(repos)}プロジェクトのドキュメント作成完了")
print(f"出力先: {output_dir}/")
