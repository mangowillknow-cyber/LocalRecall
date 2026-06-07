# LocalRecall

> 本地优先的个人 AI 工作助手 — 你的数据完全自主掌控。

LocalRecall 是一个完全运行在本地的智能知识检索工具。它会索引你电脑上的笔记、代码、文档，然后你可以用自然语言向它提问，比如 *"找出去年我研究过的 Docker 网络笔记"*。

数据永远不会离开你的电脑。

## 截图

<!-- TODO: 添加截图 -->

## 核心特性

- **完全本地运行** — 使用 Ollama 或内置 llama-cpp 推理，100% 离线可用
- **7 种数据源插件** — Markdown、代码（Tree-sitter AST 感知）、PDF、Office（docx/xlsx/pptx）、OCR 图片识别、浏览器书签、终端命令历史
- **智能语义检索** — 向量搜索（ChromaDB）+ 全文匹配，混合排序
- **自然语言查询** — 像和 AI 对话一样搜索你的数据
- **流式回答** — WebSocket 实时推送，逐字显示
- **增量索引** — watchdog 监听文件变更，修改即索引
- **暗色模式** — 自动跟随系统主题
- **Tauri 桌面应用** — 包体 ~3MB，启动快，内存占用低
- **插件系统** — 社区可扩展更多数据源（微信、Slack、Notion 等）

## 技术架构

```
┌─────────────────────────────────┐
│     Tauri (Rust) 桌面壳          │
│  ┌───────────────────────────┐  │
│  │  React + TypeScript 前端   │  │
│  └───────────────────────────┘  │
├─────────── WebSocket ───────────┤
│  ┌───────────────────────────┐  │
│  │  Python FastAPI 后端       │  │
│  │  ┌─────────┐ ┌─────────┐ │  │
│  │  │ 索引引擎 │ │ 查询引擎 │ │  │
│  │  └────┬────┘ └────┬────┘ │  │
│  │       │           │      │  │
│  │  ┌────┴────┐ ┌────┴────┐ │  │
│  │  │ChromaDB │ │ Ollama/  │ │  │
│  │  │(向量库) │ │llama-cpp │ │  │
│  │  └─────────┘ └─────────┘ │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
        ▲ watchdog 监听
        │
┌───────┴────────┐
│   本地文件系统    │
│ .md .py .js .pdf│
│ .docx .png ...  │
└────────────────┘
```

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 18+
- Rust（编译 Tauri 桌面应用）
- [Ollama](https://ollama.ai)（可选，用于 LLM 推理）

### 安装

```bash
# 克隆仓库
git clone https://github.com/mangowillknow-cyber/LocalRecall.git
cd LocalRecall

# 创建虚拟环境并安装后端依赖
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e backend/

# 安装前端依赖
cd frontend && npm install
```

### 运行

**方式一：分开启动**

```bash
# 终端 1：启动后端
cd backend && python -m app.main

# 终端 2：启动前端
cd frontend && npm run dev
```

打开 http://localhost:1420

**方式二：桌面应用**

```bash
cd frontend && npm run tauri dev
```

### 首次使用

1. 打开设置页（左侧齿轮图标）
2. 在"数据源"中添加你的笔记目录
3. 等待索引完成（状态页可查看进度）
4. 回到搜索页，用自然语言提问

## 项目结构

```
LocalRecall/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── core/              # 核心模块
│   │   │   ├── database.py    # SQLite 数据库
│   │   │   ├── vector_store.py # ChromaDB 向量存储
│   │   │   ├── indexer.py     # 索引引擎
│   │   │   ├── query_engine.py # RAG 查询引擎
│   │   │   ├── llm_manager.py # LLM 推理管理
│   │   │   └── file_watcher.py # 文件监控
│   │   ├── plugins/           # 插件系统
│   │   │   ├── base.py        # 插件抽象基类
│   │   │   ├── loader.py      # 插件动态加载器
│   │   │   └── builtin/       # 7 个内置插件
│   │   ├── routers/           # API 路由
│   │   └── main.py            # FastAPI 入口
│   └── tests/                 # 测试
├── frontend/                   # Tauri + React 前端
│   ├── src/
│   │   ├── pages/             # 5 个页面
│   │   ├── components/        # 共享组件
│   │   └── hooks/             # 自定义 Hooks
│   └── src-tauri/             # Rust Tauri 层
│       └── src/
│           ├── lib.rs
│           └── python_manager.rs
└── docs/                       # 设计文档
```

## 插件开发

实现 `DataSourcePlugin` 接口即可创建新插件：

```python
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk
from pathlib import Path

class MyPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".myext"]

    def parse(self, file_path: Path) -> ParsedDocument:
        content = file_path.read_text(encoding="utf-8")
        return ParsedDocument(
            content=content,
            metadata={"file_name": file_path.name},
            source_path=file_path,
            content_type="mytype",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        return [Chunk(text=doc.content, metadata=doc.metadata, index=0)]
```

将插件放入 `backend/app/plugins/community/` 目录即可自动加载。

## 配置

数据目录默认位置：

| 系统 | 路径 |
|------|------|
| Windows | `E:/LocalRecall` 或 `%LOCALAPPDATA%/LocalRecall` |
| Linux | `~/.localrecall` |
| macOS | `~/Library/Application Support/LocalRecall` |

可通过环境变量覆盖：

```bash
LOCALRECALL_DATA_DIR=/path/to/data python -m app.main
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [Ollama](https://ollama.ai) — 本地 LLM 推理
- [Tauri](https://tauri.app) — 跨平台桌面框架
- [ChromaDB](https://www.trychroma.com) — 向量数据库
- [sentence-transformers](https://www.sbert.net) — Embedding 模型
- [BAAI/bge-small-zh](https://huggingface.co/BAAI/bge-small-zh-v1.5) — 中文 Embedding
