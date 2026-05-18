# Power RAG Project

企业内部 RAG 知识库系统 - V1 简易版

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 直接编辑 .env 文件填入你的 API Key

# 3. 准备数据目录
mkdir -p docs repos

# 4. 启动服务
python -m app.main
```

## 配置说明

编辑 `.env` 文件：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| EMBEDDING_BASE_URL | Embedding API 地址 | https://api.openai.com/v1 |
| EMBEDDING_API_KEY | Embedding API Key | - |
| EMBEDDING_MODEL | Embedding 模型 | text-embedding-3-small |
| LLM_BASE_URL | LLM API 地址 | https://api.openai.com/v1 |
| LLM_API_KEY | LLM API Key | - |
| LLM_MODEL | LLM 模型 | gpt-4o-mini |
| SCAN_PATHS | 扫描路径（逗号分隔） | ./docs |
| SCAN_INTERVAL_MINUTES | 定时扫描间隔（分钟） | 60 |

## 支持的文件格式

| 格式 | 说明 |
|------|------|
| .md, .txt | 纯文本 |
| .pdf | PDF 文档 |
| .docx | Word 文档 |
| .java, .xml, .yaml, .yml, .sql | 代码文件 |

## 启动说明

- 首次启动会自动扫描 `SCAN_PATHS` 并建立索引
- 之后每隔 `SCAN_INTERVAL_MINUTES` 分钟自动增量扫描

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /chat | RAG 问答 |
| POST | /index/rebuild | 全量重建索引 |
| POST | /index/increment | 增量扫描 |
| GET  | /health | 健康检查 |

### 问答示例

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "订单取消逻辑在哪"}'
```

## 何时使用 rebuild

- 切换了 Embedding 模型
- 向量库数据损坏
- 数据不一致需要清理

## 架构

```
app/
├── api/          # FastAPI 路由
├── scanner/      # 文件扫描（递归、忽略目录、增量检测）
├── parser/       # 文件解析（md/txt/pdf/docx/代码）
├── chunker/      # 文本切分（文档按长度，Java按class/method）
├── embedding/    # Embedding 抽象接口 + OpenAI Compatible 实现
├── vectorstore/  # ChromaDB 封装
├── retriever/    # 向量检索
├── llm/          # LLM 问答
├── scheduler/    # 定时增量扫描 + 索引逻辑
├── config/       # 配置管理
├── models/       # 数据模型
└── main.py       # 入口
```
