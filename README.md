# RAG智能问答系统

基于本地知识库的RAG（检索增强生成）智能问答系统，支持文档上传、向量化存储和智能问答。

## 功能特性

- 📄 **文档上传**: 支持PDF、DOCX、TXT格式文档
- 📚 **知识库构建**: 自动解析、分块并构建向量数据库
- 🔍 **智能检索**: 基于FAISS的相似性检索
- 💬 **问答交互**: 基于Ollama本地大模型的智能问答
- 📝 **对话历史**: 支持多轮对话记忆

## 技术栈

- **前端**: Streamlit
- **向量数据库**: FAISS
- **向量化**: TF-IDF
- **大模型**: Ollama (deepseek-r1:7b / qwen2:7b)
- **文档处理**: PyPDF2, python-docx

## 环境要求

- Python 3.10+
- Ollama (可选，用于完整AI问答功能)

## 安装步骤

```bash
# 克隆仓库
git clone https://github.com/cnycny1/RAG-QA-System.git
cd RAG-QA-System

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 安装Ollama（可选）

1. 从 https://ollama.com/download 下载安装Ollama
2. 启动服务: `ollama serve`
3. 下载模型: `ollama pull deepseek-r1:7b`

## 使用说明

### 运行Web应用

```bash
python -m streamlit run app.py
```

### 使用流程

1. **上传文档**: 在左侧"知识库管理"区域上传PDF/DOCX/TXT文件
2. **构建知识库**: 点击"构建知识库"按钮
3. **开始问答**: 在右侧输入问题并点击"发送"

### 命令行测试

```bash
python cli_test.py
```

## 项目结构

```
├── app.py              # Streamlit Web应用
├── utils.py            # 文档加载和向量数据库操作
├── rag_chain.py        # RAG问答链实现
├── cli_test.py         # 命令行测试脚本
├── requirements.txt    # 依赖列表
├── .gitignore          # Git忽略配置
├── .streamlit/
│   └── config.toml     # Streamlit配置
└── 自然语言处理/       # 示例文档目录
    ├── nlp_introduction.txt
    ├── transformer_architecture.txt
    ├── bert_gpt_comparison.txt
    ├── word_embeddings.txt
    └── pretrained_language_models.txt
```

## RAG流程

1. **文档加载**: 读取PDF/DOCX/TXT文件内容
2. **文本分块**: 使用文本分割算法分割文本（chunk_size=1000, chunk_overlap=200）
3. **向量化**: 使用TF-IDF将文本块转换为向量
4. **存储**: 将向量存入FAISS索引
5. **检索**: 接收用户问题，检索最相关的3个文本块
6. **生成**: 将检索结果作为上下文，调用Ollama生成回答

## 示例问题

- 什么是自然语言处理？
- Transformer架构的核心组件有哪些？
- BERT和GPT有什么区别？
- 词向量的作用是什么？
- 预训练语言模型的优势是什么？

## 已知问题与改进方向

- ✅ Ollama未安装时提供文档检索回退功能
- ⬜ 支持更多文档格式（如Excel）
- ⬜ 添加文档管理功能（删除、更新）
- ⬜ 支持多语言文档
- ⬜ 添加模型选择功能

## 许可证

MIT License