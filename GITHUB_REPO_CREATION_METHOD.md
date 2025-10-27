# GitHubリポジトリ作成方法（認証トークン使用）

## 概要

Claude Codeから自動的にGitHubリポジトリを作成し、コードをプッシュする方法

## 前提条件

- Git認証情報が `.git-credentials` に保存されていること
- GitHub Personal Access Token (PAT) が含まれていること

## 認証トークンの確認

### 1. 認証情報ファイルの場所

```
C:\Users\[USERNAME]\.git-credentials
```

### 2. ファイル形式

```
https://[USERNAME]:[TOKEN]@github.com
```

**例**:
```
https://[USERNAME]:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com
```

## リポジトリ作成手順

### ステップ1: 認証トークンの読み取り

```bash
# .git-credentialsから認証情報を取得
cat C:\Users\Tenormusica\.git-credentials
```

### ステップ2: GitHub API でリポジトリ作成

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token [YOUR_TOKEN]" \
  https://api.github.com/user/repos \
  -d '{"name":"repo-name","description":"Repository description","private":false,"auto_init":false}'
```

**実際の例**:
```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  https://api.github.com/user/repos \
  -d '{"name":"voicevox-mcp-notification","description":"VOICEVOX MCP Server for Claude Code voice notifications","private":false,"auto_init":false}'
```

### ステップ3: Gitリモートの設定

```bash
cd [PROJECT_DIR]
git remote add origin https://[USERNAME]:[TOKEN]@github.com/[USERNAME]/[REPO_NAME].git
```

**実際の例**:
```bash
cd "C:\Users\[USERNAME]\voicevox-mcp-notification"
git remote add origin https://[USERNAME]:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/[USERNAME]/voicevox-mcp-notification.git
```

### ステップ4: プッシュ

```bash
git push -u origin master
```

## エラーハンドリング

### リポジトリが既に存在する場合

```json
{
  "message": "Repository creation failed.",
  "errors": [
    {
      "resource": "Repository",
      "code": "custom",
      "field": "name",
      "message": "name already exists on this account"
    }
  ],
  "status": "422"
}
```

**対処**: リモートURLを設定してプッシュのみ実行

```bash
git remote add origin https://[USERNAME]:[TOKEN]@github.com/[USERNAME]/[REPO_NAME].git
git push -u origin master
```

### リモートが既に存在する場合

```
error: remote origin already exists.
```

**対処**: リモートを削除してから再追加

```bash
git remote remove origin
git remote add origin https://[USERNAME]:[TOKEN]@github.com/[USERNAME]/[REPO_NAME].git
git push -u origin master
```

または、URLを更新:

```bash
git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/[USERNAME]/[REPO_NAME].git
git push -u origin master
```

## 完全な自動化スクリプト例

```bash
#!/bin/bash

# 変数設定
REPO_NAME="your-repo-name"
REPO_DESC="Repository description"
PROJECT_DIR="C:\Users\[USERNAME]\your-project"
USERNAME="your-github-username"
TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Step 1: GitHubリポジトリ作成
echo "Creating GitHub repository..."
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESC\",\"private\":false,\"auto_init\":false}"

# Step 2: リモート設定（既存の場合は削除）
cd "$PROJECT_DIR"
git remote remove origin 2>/dev/null || true
git remote add origin "https://$USERNAME:$TOKEN@github.com/$USERNAME/$REPO_NAME.git"

# Step 3: プッシュ
git push -u origin master

echo "✅ Repository created and code pushed successfully!"
echo "URL: https://github.com/$USERNAME/$REPO_NAME"
```

## セキュリティ注意事項

### ⚠️ トークンの取り扱い

1. **トークンを直接コードに含めない**
   - 環境変数を使用
   - `.git-credentials` から読み取る

2. **トークンの権限**
   - 必要最小限の権限のみ付与
   - `repo` スコープが必要

3. **トークンの有効期限**
   - 定期的に更新
   - 使用しないトークンは削除

### トークンの環境変数化

```bash
# トークンを環境変数に設定
export GITHUB_TOKEN="gho_xxxxxxxxxxxxx"

# 使用例
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/repos
```

## Claude Code での実装方法

### 手順

1. `.git-credentials` ファイルを読み取る
2. トークンを抽出
3. GitHub API でリポジトリ作成
4. Gitリモート設定
5. プッシュ実行

### サンプルコード（Claude Code実装）

```python
import subprocess
import re

# Step 1: トークン取得
with open(r"C:\Users\Tenormusica\.git-credentials", "r") as f:
    creds = f.read().strip()
    
# トークン抽出
match = re.search(r'https://([^:]+):([^@]+)@github\.com', creds)
username = match.group(1)
token = match.group(2)

# Step 2: リポジトリ作成
subprocess.run([
    "curl", "-X", "POST",
    "-H", "Accept: application/vnd.github.v3+json",
    "-H", f"Authorization: token {token}",
    "https://api.github.com/user/repos",
    "-d", '{"name":"my-repo","description":"My project","private":false}'
])

# Step 3: プッシュ
subprocess.run([
    "git", "remote", "add", "origin",
    f"https://{username}:{token}@github.com/{username}/my-repo.git"
], cwd=project_dir)

subprocess.run(["git", "push", "-u", "origin", "master"], cwd=project_dir)
```

## トラブルシューティング

### 認証エラー

```json
{
  "message": "Bad credentials",
  "status": "401"
}
```

**原因**: トークンが無効または期限切れ  
**対処**: 新しいトークンを生成

### リポジトリが見つからない

```
fatal: repository 'https://github.com/xxx/xxx.git/' not found
```

**原因**: リポジトリがまだ作成されていない  
**対処**: GitHub API でリポジトリ作成を確認

## 参考リンク

- [GitHub REST API - Repositories](https://docs.github.com/en/rest/repos/repos)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Git Credential Storage](https://git-scm.com/docs/git-credential-store)

## 実際の使用例（2025-10-27）

**プロジェクト**: voicevox-mcp-notification

### 実行コマンド

```bash
# 1. トークン確認
cat C:\Users\[USERNAME]\.git-credentials
# => https://[USERNAME]:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com

# 2. リポジトリ作成試行（既に存在）
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  https://api.github.com/user/repos \
  -d '{"name":"voicevox-mcp-notification","description":"VOICEVOX MCP Server for Claude Code voice notifications","private":false,"auto_init":false}'

# 3. リモート設定
cd "C:\Users\[USERNAME]\voicevox-mcp-notification"
git remote add origin https://[USERNAME]:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/[USERNAME]/voicevox-mcp-notification.git

# 4. プッシュ成功
git push -u origin master
# => To https://github.com/[USERNAME]/voicevox-mcp-notification.git
# => * [new branch]      master -> master
```

### 結果

✅ リポジトリ作成・プッシュ成功  
📍 URL: https://github.com/[USERNAME]/voicevox-mcp-notification

**注意**: 実際の使用時は上記の `[USERNAME]` と `ghp_xxxx...` を実際の値に置き換えてください。

---

**作成日**: 2025-10-27  
**プロジェクト**: devrag-local-project-rag  
**カテゴリ**: GitHub自動化・認証
