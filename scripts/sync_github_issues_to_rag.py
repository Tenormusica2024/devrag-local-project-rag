#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Issues to Local RAG Sync Script
毎日1回GitHub Issueの最新20コメントを取得してローカルRAGに転記
"""

import os
import sys
import io
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# UTF-8エンコーディング設定（Windows環境対応）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'buffer') else sys.stdout
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace') if hasattr(sys.stderr, 'buffer') else sys.stderr

# 設定
ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT.parent / "Documents" / "github-remote-desktop" / ".env_private"

# 環境変数読み込み
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE, override=True)
except:
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = "Tenormusica2024/Private"
ISSUE_NUMBERS = [1, 2, 3, 4]
COMMENTS_PER_ISSUE = 20

# RAGドキュメント出力先
DOCUMENTS_DIR = ROOT.parent / "documents" / "github-issues"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# 前回取得状態ファイル
STATE_FILE = ROOT / "scripts" / "last_sync_state.json"

API_BASE = "https://api.github.com"

def load_last_sync_state():
    """前回の同期状態を読み込み"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sync_state(state):
    """同期状態を保存"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def fetch_issue_comments(issue_number, per_page=20):
    """指定されたIssueの最新コメントを取得"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/issues/{issue_number}/comments"
    params = {
        "per_page": per_page,
        "sort": "created",
        "direction": "desc"
    }
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Issue #{issue_number} comments: {e}")
        return []

def format_comment_to_markdown(comment, issue_number):
    """コメントをマークダウン形式に変換"""
    created_at = comment.get('created_at', '')
    author = comment.get('user', {}).get('login', 'Unknown')
    body = comment.get('body', '')
    comment_url = comment.get('html_url', '')
    
    markdown = f"""---
**Issue**: #{issue_number}  
**Author**: @{author}  
**Date**: {created_at}  
**URL**: {comment_url}

---

{body}

---
"""
    return markdown

def sync_issue_to_rag(issue_number):
    """指定されたIssueのコメントをRAGに同期"""
    print(f"\n=== Issue #{issue_number} 同期開始 ===")
    
    # 最新コメント取得
    comments = fetch_issue_comments(issue_number, COMMENTS_PER_ISSUE)
    
    if not comments:
        print(f"Issue #{issue_number}: コメントなし")
        return False
    
    print(f"取得コメント数: {len(comments)}件")
    
    # マークダウンファイル作成
    output_file = DOCUMENTS_DIR / f"issue_{issue_number}_latest_comments.md"
    
    # ヘッダー部分
    content = f"""# Private Repository Issue #{issue_number} - 最新コメント

**リポジトリ**: {GITHUB_REPO}  
**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**コメント数**: {len(comments)}件

---

## 最新コメント一覧

"""
    
    # 各コメントを追加
    for i, comment in enumerate(comments, 1):
        content += f"### コメント #{i}\n\n"
        content += format_comment_to_markdown(comment, issue_number)
        content += "\n"
    
    # ファイル書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 保存完了: {output_file}")
    return True

def run_devrag_index():
    """devragインデックス再作成を自動実行"""
    devrag_exe = ROOT.parent / "devrag-windows-x64.exe"
    
    if not devrag_exe.exists():
        print(f"⚠️  devrag実行ファイルが見つかりません: {devrag_exe}")
        print("   手動でインデックス作成が必要です")
        return False
    
    print()
    print("=" * 60)
    print("📌 devragインデックス自動作成を開始...")
    print("=" * 60)
    
    try:
        # devrag indexコマンドを実行
        result = subprocess.run(
            [str(devrag_exe), "index"],
            cwd=str(ROOT.parent),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300  # 5分タイムアウト
        )
        
        # 標準出力を表示
        if result.stdout:
            print(result.stdout)
        
        # 標準エラー出力を表示
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ devragインデックス作成完了")
            return True
        else:
            print(f"❌ devragインデックス作成失敗（終了コード: {result.returncode}）")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ devragインデックス作成がタイムアウトしました（5分経過）")
        return False
    except Exception as e:
        print(f"❌ devragインデックス作成中にエラー: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("GitHub Issues to Local RAG Sync")
    print("=" * 60)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"対象リポジトリ: {GITHUB_REPO}")
    print(f"対象Issue: {ISSUE_NUMBERS}")
    print(f"取得コメント数/Issue: {COMMENTS_PER_ISSUE}件")
    print()
    
    # 前回の同期状態読み込み
    last_state = load_last_sync_state()
    current_state = {}
    
    # 各Issueを同期
    success_count = 0
    for issue_num in ISSUE_NUMBERS:
        try:
            if sync_issue_to_rag(issue_num):
                success_count += 1
                current_state[f"issue_{issue_num}"] = datetime.now().isoformat()
        except Exception as e:
            print(f"❌ Issue #{issue_num} 同期失敗: {e}")
    
    # 同期状態保存
    save_sync_state(current_state)
    
    print()
    print("=" * 60)
    print(f"同期完了: {success_count}/{len(ISSUE_NUMBERS)} Issues")
    print(f"出力先: {DOCUMENTS_DIR}")
    print("=" * 60)
    
    # devragインデックス自動作成
    devrag_success = run_devrag_index()
    
    print()
    print("=" * 60)
    print("🎯 完了サマリー")
    print("=" * 60)
    print(f"✅ GitHub Issue同期: {success_count}/{len(ISSUE_NUMBERS)} 成功")
    print(f"{'✅' if devrag_success else '❌'} devragインデックス作成: {'成功' if devrag_success else '失敗'}")
    print()
    if devrag_success:
        print("📝 Claude Codeを再起動して変更を反映してください")
    else:
        print("📝 手動でdevragインデックス作成が必要です:")
        print(f"   cd C:\\Users\\Tenormusica")
        print(f"   .\\devrag-windows-x64.exe index")
    print("=" * 60)

if __name__ == "__main__":
    main()
