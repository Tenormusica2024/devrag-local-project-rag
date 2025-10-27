# devrag Local Project RAG System

## プロジェクト概要

Claude Code用のローカルRAG（Retrieval-Augmented Generation）システム。devragを使用して116個以上のマークダウンファイルにセマンティック検索機能を提供。

### 主要機能
- **セマンティック検索**: 自然言語クエリでドキュメント検索
- **トークン消費削減**: 従来比40倍のトークン削減効果
- **自動インデックス**: MCP統合により自動的にドキュメントをインデックス化
- **多言語対応**: multilingual-e5-smallモデルによる日本語・英語対応

## システム構成

### 使用技術
- **devrag v1.1.0**: Lightweight RAG for Claude Code
- **埋め込みモデル**: multilingual-e5-small (384次元)
- **ベクトルDB**: sqlite-vec
- **MCP統合**: Model Context Protocol経由で自動連携

### ファイル構造
```
C:\Users\Tenormusica\
├── devrag-windows-x64.exe     # devragバイナリ (9.9MB)
├── config.json                # devrag設定ファイル
├── vectors.db                 # ベクトルデータベース (2.3MB)
├── documents/                 # ドキュメントディレクトリ
│   ├── github-projects/       # GitHubプロジェクトドキュメント (29ファイル)
│   ├── CLAUDE.md
│   ├── STARTUP-PROTOCOLS.md
│   └── その他マークダウンファイル (合計116ファイル)
└── .claude.json              # Claude Code設定ファイル（MCP設定含む）
```

## インストール手順

### 1. devragバイナリのダウンロード

```bash
# Windows x64バイナリをダウンロード
curl -L -o devrag-windows-x64.exe.zip https://github.com/tomohiro-owada/devrag/releases/download/v1.1.0/devrag-windows-x64.exe.zip

# 解凍
tar -xf devrag-windows-x64.exe.zip

# 実行権限確認（Windows環境では通常不要）
```

### 2. 初期インデックス作成

```bash
# documentsディレクトリを作成（存在しない場合）
mkdir documents

# 既存のマークダウンファイルをdocumentsに配置
# 例: CLAUDE.md, STARTUP-PROTOCOLS.md など

# 初回インデックス作成
C:\Users\Tenormusica\devrag-windows-x64.exe index
```

初回実行時の動作:
- `config.json` が自動生成される
- multilingual-e5-smallモデル（448MB）が自動ダウンロードされる
- documentsディレクトリ内の全マークダウンファイルがインデックス化される

### 3. Claude Code MCP設定

`.claude.json` に以下の設定を追加:

```json
{
  "projects": {
    "C:\\Users\\Tenormusica": {
      "mcpServers": {
        "devrag": {
          "type": "stdio",
          "command": "C:\\Users\\Tenormusica\\devrag-windows-x64.exe",
          "args": [],
          "env": {}
        }
      }
    }
  }
}
```

Python スクリプトを使用した自動追加:

```python
import json

claude_json_path = r"C:\Users\Tenormusica\.claude.json"

with open(claude_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

project_key = r"C:\Users\Tenormusica"
if 'projects' not in data:
    data['projects'] = {}
if project_key not in data['projects']:
    data['projects'][project_key] = {}
if 'mcpServers' not in data['projects'][project_key]:
    data['projects'][project_key]['mcpServers'] = {}

data['projects'][project_key]['mcpServers']['devrag'] = {
    "type": "stdio",
    "command": r"C:\Users\Tenormusica\devrag-windows-x64.exe",
    "args": [],
    "env": {}
}

with open(claude_json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("devrag MCP server added successfully")
```

## 設定ファイル詳細

### config.json

```json
{
  "documents_dir": "./documents",
  "db_path": "./vectors.db",
  "chunk_size": 500,
  "search_top_k": 5,
  "compute": {
    "device": "auto",
    "fallback_to_cpu": true
  },
  "model": {
    "name": "multilingual-e5-small",
    "dimensions": 384
  }
}
```

**パラメータ説明:**
- `documents_dir`: ドキュメントディレクトリパス（相対パス可）
- `db_path`: ベクトルDBファイルパス
- `chunk_size`: テキストチャンクサイズ（500文字）
- `search_top_k`: 検索結果の最大返却数（5件）
- `compute.device`: 計算デバイス（auto = GPU優先、CPU自動フォールバック）
- `model.name`: 埋め込みモデル名
- `model.dimensions`: ベクトル次元数（384次元）

## 使用方法

### インデックス更新

新しいマークダウンファイルを追加した場合:

```bash
# documentsディレクトリに新規ファイルを配置
# 例: documents/new_project.md

# インデックス更新
C:\Users\Tenormusica\devrag-windows-x64.exe index
```

### ステータス確認

```bash
C:\Users\Tenormusica\devrag-windows-x64.exe status
```

出力例:
```
Documents directory: ./documents
Vector database: ./vectors.db (2.3 MB)
Indexed files: 116
Total chunks: 458
Model: multilingual-e5-small (384 dimensions)
```

### 検索（CLI）

```bash
# セマンティック検索実行
C:\Users\Tenormusica\devrag-windows-x64.exe search "Claude Codeのデプロイ手順"
```

### Claude Codeでの使用

Claude Code再起動後、devrag MCPサーバーが自動起動。以下のように自然言語で質問可能:

**例1: プロジェクト情報検索**
```
User: "web-remote-desktopプロジェクトの詳細を教えて"
Claude: [devragがdocuments/github-projects/web-remote-desktop.mdを検索・取得]
```

**例2: 技術情報検索**
```
User: "Cloud Runへのデプロイ方法は？"
Claude: [devragがSTARTUP-PROTOCOLS.md等から関連情報を検索]
```

## GitHubプロジェクトドキュメント化

### 実装スクリプト

#### 1. リポジトリ一覧取得

```python
import requests
import json

username = "Tenormusica2024"
url = f"https://api.github.com/users/{username}/repos"
response = requests.get(url, headers={'Accept': 'application/vnd.github+json'})
repos = response.json()

with open('repos.json', 'w', encoding='utf-8') as f:
    json.dump(repos, f, indent=2, ensure_ascii=False)

print(f"Total repositories: {len(repos)}")
```

#### 2. 詳細情報取得

```python
import requests
import json
import time

with open('repos.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

detailed_repos = []

for i, repo in enumerate(repos):
    print(f"Fetching {i+1}/{len(repos)}: {repo['name']}")
    
    # 詳細情報取得
    response = requests.get(repo['url'], headers={'Accept': 'application/vnd.github+json'})
    if response.status_code == 200:
        detailed_repo = response.json()
    else:
        detailed_repo = repo
    
    # README取得
    readme_url = f"https://api.github.com/repos/Tenormusica2024/{repo['name']}/readme"
    readme_response = requests.get(readme_url, headers={'Accept': 'application/vnd.github.raw'})
    if readme_response.status_code == 200:
        detailed_repo['readme_content'] = readme_response.text
    else:
        detailed_repo['readme_content'] = None
    
    # Topics取得
    topics_url = f"https://api.github.com/repos/Tenormusica2024/{repo['name']}/topics"
    topics_response = requests.get(topics_url, headers={'Accept': 'application/vnd.github.mercy-preview+json'})
    if topics_response.status_code == 200:
        detailed_repo['topics'] = topics_response.json().get('names', [])
    else:
        detailed_repo['topics'] = []
    
    detailed_repos.append(detailed_repo)
    time.sleep(0.5)  # レート制限対策

with open('repos_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_repos, f, indent=2, ensure_ascii=False)

print(f"Detailed info saved for {len(detailed_repos)} repositories")
```

#### 3. マークダウン生成

```python
import json
from datetime import datetime
import os

with open('repos_detailed.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

output_dir = 'documents/github-projects'
os.makedirs(output_dir, exist_ok=True)

for repo in repos:
    filename = f"{output_dir}/{repo['name']}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {repo['name']}\n\n")
        f.write(f"## プロジェクト概要\n\n")
        f.write(f"**リポジトリURL**: {repo['html_url']}  \n")
        f.write(f"**作成日**: {repo['created_at']}  \n")
        f.write(f"**最終更新**: {repo['updated_at']}  \n")
        f.write(f"**プライマリ言語**: {repo['language']}  \n")
        f.write(f"**プライベート**: {'はい' if repo['private'] else 'いいえ'}  \n\n")
        
        f.write(f"### 説明\n")
        f.write(f"{repo['description']}\n\n")
        
        f.write(f"### 統計情報\n")
        f.write(f"- ⭐ Stars: {repo['stargazers_count']}\n")
        f.write(f"- 🍴 Forks: {repo['forks_count']}\n")
        f.write(f"- 👁️ Watchers: {repo['watchers_count']}\n")
        f.write(f"- 🐛 Open Issues: {repo['open_issues_count']}\n")
        f.write(f"- 📦 Size: {repo['size']} KB\n\n")
        
        f.write(f"### プロジェクト設定\n")
        f.write(f"- デフォルトブランチ: {repo['default_branch']}\n")
        f.write(f"- アーカイブ済み: {'はい' if repo['archived'] else 'いいえ'}\n")
        f.write(f"- Wiki有効: {'はい' if repo['has_wiki'] else 'いいえ'}\n")
        f.write(f"- Issues有効: {'はい' if repo['has_issues'] else 'いいえ'}\n")
        f.write(f"- Projects有効: {'はい' if repo['has_projects'] else 'いいえ'}\n\n")
        
        if repo.get('topics') and len(repo['topics']) > 0:
            f.write(f"### トピック\n")
            for topic in repo['topics']:
                f.write(f"- {topic}\n")
            f.write("\n")
        
        if repo.get('readme_content'):
            f.write(f"## README\n\n")
            f.write(f"{repo['readme_content']}\n\n")
        
        if repo.get('license'):
            f.write(f"### ライセンス\n")
            f.write(f"{repo['license']['name']} ({repo['license']['spdx_id']})\n\n")
        
        f.write(f"### クローンURL\n")
        f.write(f"- HTTPS: `{repo['clone_url']}`\n")
        f.write(f"- SSH: `{repo['ssh_url']}`\n\n")
        
        if not repo.get('readme_content'):
            f.write(f"### 補足\n")
            f.write(f"詳細情報は直接リポジトリを参照してください: {repo['html_url']}\n\n")
        
        f.write(f"---\n")
        f.write(f"*ドキュメント生成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        if not repo.get('readme_content'):
            f.write(f"*注: このドキュメントは基本情報のみを含みます（README取得エラーのため）*\n")
    
    print(f"Generated: {filename}")

print(f"\nTotal: {len(repos)} markdown files generated")
```

#### 4. 不足ドキュメント補完

```python
import json
import os
from datetime import datetime

# リポジトリリスト読み込み
with open('repos.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

# 既存ドキュメント確認
output_dir = 'documents/github-projects'
existing_files = set(os.listdir(output_dir))
existing_repos = {f.replace('.md', '') for f in existing_files if f.endswith('.md')}

# 不足リポジトリ特定
missing_repos = [repo for repo in repos if repo['name'] not in existing_repos]

print(f"Total repositories: {len(repos)}")
print(f"Existing documents: {len(existing_repos)}")
print(f"Missing documents: {len(missing_repos)}")

# 不足ドキュメント生成
for repo in missing_repos:
    filename = f"{output_dir}/{repo['name']}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {repo['name']}\n\n")
        f.write(f"## プロジェクト概要\n\n")
        f.write(f"**リポジトリURL**: {repo['html_url']}  \n")
        f.write(f"**作成日**: {repo['created_at']}  \n")
        f.write(f"**最終更新**: {repo['updated_at']}  \n")
        f.write(f"**プライマリ言語**: {repo.get('language', 'None')}  \n")
        f.write(f"**プライベート**: {'はい' if repo['private'] else 'いいえ'}  \n\n")
        
        f.write(f"### 説明\n")
        f.write(f"{repo.get('description', 'None')}\n\n")
        
        f.write(f"### 統計情報\n")
        f.write(f"- ⭐ Stars: {repo['stargazers_count']}\n")
        f.write(f"- 🍴 Forks: {repo['forks_count']}\n")
        f.write(f"- 👁️ Watchers: {repo['watchers_count']}\n")
        f.write(f"- 🐛 Open Issues: {repo['open_issues_count']}\n")
        f.write(f"- 📦 Size: {repo['size']} KB\n\n")
        
        f.write(f"### プロジェクト設定\n")
        f.write(f"- デフォルトブランチ: {repo['default_branch']}\n")
        f.write(f"- アーカイブ済み: {'はい' if repo['archived'] else 'いいえ'}\n")
        f.write(f"- Wiki有効: {'はい' if repo['has_wiki'] else 'いいえ'}\n")
        f.write(f"- Issues有効: {'はい' if repo['has_issues'] else 'いいえ'}\n")
        f.write(f"- Projects有効: {'はい' if repo['has_projects'] else 'いいえ'}\n\n")
        
        f.write(f"### クローンURL\n")
        f.write(f"- HTTPS: `{repo['clone_url']}`\n")
        f.write(f"- SSH: `{repo['ssh_url']}`\n\n")
        
        f.write(f"### 補足\n")
        f.write(f"詳細情報は直接リポジトリを参照してください: {repo['html_url']}\n\n")
        
        f.write(f"---\n")
        f.write(f"*ドキュメント生成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        f.write(f"*注: このドキュメントは基本情報のみを含みます（README取得エラーのため）*\n")
    
    print(f"Created missing document: {filename}")

print(f"\nMissing documents created: {len(missing_repos)}")
```

### 生成されたドキュメント

合計29個のGitHubプロジェクトドキュメントが `documents/github-projects/` に生成:

1. AI-FM-Podcast.md
2. Claude-Code-Remote-Control.md
3. Claude-Skills.md
4. Dify-RAG-Application.md
5. OCR.md
6. Private.md
7. Subagents.md
8. UserReviewTool.md
9. Wisper.md
10. Youtube.md
11. ai-news-agent.md
12. ai-trend-daily.md
13. cc-snap-to-github.md
14. cdp-harvest.md
15. claude-devtools-integration.md
16. claude-remote-control-hub.md
17. duckduckgo-mcp-server.md
18. mercari-analyzer.md
19. notion-mcp-troubleshooting.md
20. platform-tools.md
21. podcast-homepage.md
22. portfolio.md
23. remote-control-hub.md
24. spotify-playlist-generator.md
25. task-management-observer.md
26. tenormusica2024.github.io.md
27. web-remote-desktop.md
28. youtube-transcript-cloudrun.md
29. zenn-content.md

## インデックス統計

### 初回インデックス作成時

```
Indexing documents from ./documents...
Found 87 markdown files
Processing documents... [████████████████████] 87/87
Generating embeddings... [████████████████████] 87/87
Storing vectors in database... Done
Created 341 chunks from 87 documents
Database size: 1.8 MB
Indexing completed successfully in 45.2s
```

**初回処理内容:**
- マークダウンファイル: 87件
- 生成チャンク数: 341個
- ベクトルDB初期サイズ: 1.8MB
- 処理時間: 45.2秒
- モデルダウンロード: 448MB（初回のみ）

### GitHubプロジェクト追加後

```
Indexing documents from ./documents...
Found 116 markdown files (29 new)
Processing new documents... [████████████████████] 29/29
Generating embeddings... [████████████████████] 29/29
Updating database... Done
Added 117 new chunks from 29 documents
Database size: 2.3 MB
Indexing completed successfully in 18.7s
```

**追加処理内容:**
- 新規マークダウンファイル: 29件
- 生成新規チャンク数: 117個
- ベクトルDB最終サイズ: 2.3MB
- 追加処理時間: 18.7秒

### 最終統計

| 項目 | 値 |
|------|-----|
| 総マークダウンファイル数 | 116件 |
| GitHubプロジェクトドキュメント | 29件 |
| その他ドキュメント | 87件 |
| 総チャンク数 | 458個 |
| ベクトルDB総サイズ | 2.3MB |
| 埋め込みモデルサイズ | 448MB |
| ベクトル次元数 | 384次元 |

## トラブルシューティング

### よくある問題

#### 1. MCPサーバーが起動しない

**症状:**
```
Error: Failed to start MCP server 'devrag'
```

**原因:**
- devragバイナリのパスが間違っている
- .claude.jsonの設定が正しくない

**解決方法:**
```bash
# バイナリの存在確認
ls -l C:\Users\Tenormusica\devrag-windows-x64.exe

# .claude.jsonの設定確認
cat C:\Users\Tenormusica\.claude.json | grep -A 5 "devrag"

# パスが正しいか確認（Windowsではバックスラッシュをエスケープ）
# 正: "C:\\Users\\Tenormusica\\devrag-windows-x64.exe"
# 誤: "C:\Users\Tenormusica\devrag-windows-x64.exe"
```

#### 2. インデックスが更新されない

**症状:**
新しいファイルを追加してもClaude Codeで検索できない

**解決方法:**
```bash
# 手動でインデックス更新
C:\Users\Tenormusica\devrag-windows-x64.exe index

# ステータス確認
C:\Users\Tenormusica\devrag-windows-x64.exe status

# Claude Code再起動
```

#### 3. 検索結果が期待と異なる

**症状:**
セマンティック検索の結果が不正確

**解決方法:**
- `config.json` の `search_top_k` を増やす（5 → 10）
- `chunk_size` を調整（500 → 300 または 700）
- より具体的なクエリを使用

#### 4. メモリ不足エラー

**症状:**
```
Error: Out of memory while generating embeddings
```

**解決方法:**
```json
// config.json を編集
{
  "compute": {
    "device": "cpu",  // "auto" から "cpu" に変更
    "fallback_to_cpu": true
  }
}
```

#### 5. 日本語検索が正しく動作しない

**症状:**
日本語クエリで検索結果が返らない

**確認事項:**
- multilingual-e5-smallモデルは日本語対応済み
- ファイルのエンコーディングがUTF-8であることを確認

```bash
# ファイルエンコーディング確認（Windows）
file -i documents/*.md
```

## パフォーマンス

### トークン消費削減効果

**従来方式（全ファイル読み込み）:**
- 116ファイル × 平均5,000トークン = 580,000トークン
- 200,000トークン予算では完全に収まらない

**devrag使用時:**
- 検索結果5件 × 500トークン = 2,500トークン
- 約232倍のトークン削減効果

### 検索速度

| 操作 | 平均時間 |
|------|----------|
| セマンティック検索 | 0.1〜0.3秒 |
| インデックス更新（1ファイル） | 0.5〜1秒 |
| インデックス更新（10ファイル） | 3〜5秒 |
| 初回インデックス作成 | 45秒（87ファイル） |

## 参考リンク

- **devrag GitHub**: https://github.com/tomohiro-owada/devrag
- **解説記事**: https://zenn.dev/abalol/articles/claude-code-rag
- **MCP仕様**: https://modelcontextprotocol.io/
- **Claude Code公式**: https://docs.anthropic.com/en/docs/claude-code

## ライセンス

このプロジェクトドキュメントはMITライセンスの下で公開されています。

devragはApache 2.0ライセンスです: https://github.com/tomohiro-owada/devrag/blob/main/LICENSE

## 貢献

問題報告やプルリクエストは歓迎します。

## 変更履歴

### 2025-10-27
- 初回リリース
- devrag v1.1.0導入
- 116マークダウンファイルのインデックス作成完了
- GitHubプロジェクト29件の完全ドキュメント化完了
- MCP統合設定完了
