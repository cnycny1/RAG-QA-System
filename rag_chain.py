import subprocess

SYSTEM_PROMPT = """
你是一个基于参考文档回答问题的助手。请根据提供的参考文档内容来回答用户的问题。

参考文档:
{context}

用户问题:
{question}

回答要求:
1. 仔细阅读并理解参考文档中的内容
2. 如果文档中包含与问题相关的信息，请基于文档内容进行回答
3. 如果文档中没有找到相关答案，请明确回复"文档中未找到相关答案"
4. 回答要简洁明了，直接针对问题

回答:
"""

def get_ollama_response(prompt, model="deepseek-r1:7b"):
    try:
        cmd = ["ollama", "chat", "-m", model, "-p", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except subprocess.TimeoutExpired:
        return "Ollama请求超时，请检查网络连接或重试"
    except FileNotFoundError:
        return "❌ Ollama未安装或未启动。请先安装Ollama并启动服务：\n\n1. 从 https://ollama.com/download 下载安装Ollama\n2. 运行命令: ollama serve\n3. 下载模型: ollama pull deepseek-r1:7b"
    except Exception as e:
        return f"Ollama调用失败: {str(e)}"

def simple_rag_query(db, question, top_k=3):
    from utils import search_similar
    
    if db is None:
        return "❌ 知识库尚未构建。请先上传文档并点击'构建知识库'按钮。"
    
    results = search_similar(db, question, top_k)
    
    if not results:
        return "文档中未找到相关答案"
    
    context = "\n\n".join([r["document"] for r in results])
    
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    
    response = get_ollama_response(prompt)
    
    if response:
        if "❌" in response or "Ollama" in response or "超时" in response:
            summary = "根据文档内容，以下是相关信息：\n\n"
            for i, r in enumerate(results, 1):
                summary += f"【参考{i}】{r['document'][:200]}...\n\n"
            summary += "\n💡 提示：为获得更好的问答体验，请安装Ollama本地大模型。"
            return summary
        if "文档中未找到相关答案" in response:
            return "文档中未找到相关答案"
        return response
    else:
        return "文档中未找到相关答案"