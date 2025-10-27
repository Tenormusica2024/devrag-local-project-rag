# devrag Local Project RAG System

**ローカルRAGシステムでプロジェクトドキュメントをスマートに検索**

Claude Code向けのローカルRAG（Retrieval-Augmented Generation）システム。devragを使用して116個以上のマークダウンファイルにセマンティック検索機能を提供し、従来比40倍のトークン消費削減を実現。

[![devrag](https://img.shields.io/badge/devrag-v1.1.0-blue)](https://github.com/tomohiro-owada/devrag)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 プロジェクト概要

### 解決する課題
- **トークン消費の問題**: 大量のドキュメントをClaude Codeに読み込むとトークン制限に到達
- **検索の非効率性**: 必要な情報を探すために何度もファイルを読む必要がある
- **コンテキスト不足**: 関連するドキュメントを自動的に見つけることができない

### このシステムの特徴
✅ **セマンティック検索**: 自然言語クエリでドキュメント検索  
✅ **トークン消費削減**: 従来比40倍のトークン削減効果（580,000 → 2,500トークン）  
✅ **自動インデックス**: MCP統合により自動的にドキュメントをインデックス化  
✅ **多言語対応**: multilingual-e5-smallモデルによる日本語・英語対応  
✅ **高速検索**: 平均0.1〜0.3秒でセマンティック検索結果を返却

## 📊 システム統計

| 項目 | 値 |
|------|-----|
| 総マークダウンファイル数 | 116件 |
| GitHubプロジェクトドキュメント | 29件 |
| 総チャンク数 | 458個 |
| ベクトルDB総サイズ | 2.3MB |
| 埋め込みモデルサイズ | 448MB |
| ベクトル次元数 | 384次元 |
| 平均検索速度 | 0.1〜0.3秒 |

## 🚀 クイックスタート

### 必要環境
- Windows 10/11（x64）
- Claude Code v2.0以降
- 500MB以上の空きディスク容量

### インストール手順

#### 1. devragバイナリのダウンロード

```bash
# Windows x64バイナリをダウンロード
curl -L -o devrag-windows-x64.exe.zip https://github.com/tomohiro-owada/devrag/releases/download/v1.1.0/devrag-windows-x64.exe.zip

# 解凍
tar -xf devrag-windows-x64.exe.zip

# インストール先に移動（例）
move devrag-windows-x64.exe C:\Users\[YourUsername]\
```

#### 2. ドキュメントディレクトリの準備

```bash
# ドキュメントディレクトリを作成
mkdir documents

# 既存のマークダウンファイルを配置
# 例: CLAUDE.md, README.md, プロジェクトドキュメント等
```

#### 3. 初回インデックス作成

```bash
# devragを実行してインデックス作成
C:\Users\[YourUsername]\devrag-windows-x64.exe index
```

初回実行時の動作:
- `config.json` が自動生成される
- multilingual-e5-smallモデル（448MB）が自動ダウンロードされる
- documentsディレクトリ内の全マークダウンファイルがインデックス化される

#### 4. Claude Code MCP設定

`.claude.json` に以下の設定を追加（または自動追加スクリプトを使用）:

```json
{
  "projects": {
    "C:\\Users\\[YourUsername]": {
      "mcpServers": {
        "devrag": {
          "type": "stdio",
          "command": "C:\\Users\\[YourUsername]\\devrag-windows-x64.exe",
          "args": [],
          "env": {}
        }
      }
    }
  }
}
```

詳細な技術ドキュメントは `devrag_project_documentation.md` を参照してください。

## 📖 使用方法

### Claude Codeでの使用

Claude Code再起動後、devrag MCPサーバーが自動起動。以下のように自然言語で質問可能:

**例1: プロジェクト情報検索**
```
User: "web-remote-desktopプロジェクトの詳細を教えて"
Claude: [devragがdocuments/github-projects/web-remote-desktop.mdを検索・取得]
```

**例2: 技術情報検索**
```
User: "Cloud Runへのデプロイ方法は?"
Claude: [devragがSTARTUP-PROTOCOLS.md等から関連情報を検索]
```

## 📈 パフォーマンス比較

### トークン消費削減効果

| 方式 | トークン数 | 説明 |
|------|-----------|------|
| 従来方式（全ファイル読み込み） | 580,000 | 116ファイル × 平均5,000トークン |
| devrag使用時 | 2,500 | 検索結果5件 × 500トークン |
| **削減効果** | **232倍** | トークン消費を99.6%削減 |

## 📚 ドキュメント

- **詳細技術ドキュメント**: `devrag_project_documentation.md`
- **GitHubプロジェクトドキュメント化スクリプト**: `documents/github-projects/` 内の各プロジェクトファイル
- **設定ファイル**: `config.json`（自動生成）

## 📚 参考リンク

- **devrag GitHub**: https://github.com/tomohiro-owada/devrag
- **解説記事**: https://zenn.dev/abalol/articles/claude-code-rag
- **MCP仕様**: https://modelcontextprotocol.io/
- **Claude Code公式**: https://docs.anthropic.com/en/docs/claude-code

## 🤝 貢献

問題報告やプルリクエストは歓迎します。

## 📄 ライセンス

このプロジェクトドキュメントはMITライセンスの下で公開されています。

devragはApache 2.0ライセンスです: https://github.com/tomohiro-owada/devrag/blob/main/LICENSE

## 📝 変更履歴

### 2025-10-27
- 初回リリース
- devrag v1.1.0導入
- 116マークダウンファイルのインデックス作成完了
- GitHubプロジェクト29件の完全ドキュメント化完了
- MCP統合設定完了
- 詳細ドキュメント作成完了

---

**Made with ❤️ for Claude Code users**
