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
4. 回答要简洁明了，直接针对问题，不要包含无关内容
5. 如果有多个相关点，请用列表形式清晰列出

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
        return None
    except Exception as e:
        return None

def extract_relevant_content(text, question, max_length=500):
    keywords = ["应用场景", "发展历程", "主要任务", "挑战", "优势", "区别", "架构", "核心组件", "功能", "特点", "作用", "定义", "概念"]
    
    for keyword in keywords:
        if keyword in question:
            start_idx = text.find(keyword)
            if start_idx != -1:
                end_idx = text.find("、", start_idx + 30)
                if end_idx == -1:
                    end_idx = text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = min(start_idx + max_length, len(text))
                return text[start_idx:end_idx].strip()
    
    lines = text.split("\n")
    result_lines = []
    
    question_tokens = question.replace("？", "").replace("?", "").replace("的", " ").split()
    
    for line in lines:
        if any(token in line for token in question_tokens):
            result_lines.append(line.strip())
        elif len(result_lines) > 0 and line.strip() and not line.strip()[0].isdigit():
            result_lines.append(line.strip())
    
    return "\n".join(result_lines)[:max_length]

def simple_rag_query(db, question, top_k=3):
    from utils import search_similar
    
    if db is None:
        return "❌ 知识库尚未构建。请先上传文档并点击'构建知识库'按钮。"
    
    results = search_similar(db, question, k=top_k)
    
    if not results:
        return "文档中未找到相关答案"
    
    context = "\n\n".join([r["document"] for r in results])
    
    response = get_ollama_response(SYSTEM_PROMPT.format(context=context, question=question))
    
    if response and "文档中未找到相关答案" not in response:
        return response
    
    answer = f"**{question}**\n\n"
    used_sources = set()
    
    for i, r in enumerate(results, 1):
        source = r["metadata"]["source"]
        if source in used_sources:
            continue
        
        relevant = extract_relevant_content(r["document"], question)
        
        if relevant:
            used_sources.add(source)
            answer += f"**【{source}】**\n{relevant}\n\n"
    
    if len(used_sources) == 0:
        answer += "文档中未找到相关答案"
    
    return answer