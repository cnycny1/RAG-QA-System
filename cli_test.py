import os
import sys
from utils import load_documents_from_folder, create_vector_db, load_vector_db, get_documents_count, search_similar
from rag_chain import simple_rag_query

def main():
    print("=== RAG智能问答系统 - 命令行测试版 ===")
    
    documents_folder = "./documents"
    persist_directory = "./chroma_db"
    
    if not os.path.exists(documents_folder):
        os.makedirs(documents_folder)
        print(f"创建文档目录: {documents_folder}")
    
    docs = load_documents_from_folder(documents_folder)
    print(f"找到 {len(docs)} 个文档")
    
    if docs:
        print("\n正在构建向量数据库...")
        vectordb = create_vector_db(docs, persist_directory)
        print(f"向量数据库构建完成，共 {get_documents_count(vectordb)} 个文本块")
    else:
        vectordb = load_vector_db(persist_directory)
        if vectordb:
            print(f"加载现有向量数据库，共 {get_documents_count(vectordb)} 个文本块")
        else:
            print("未找到文档和向量数据库，请先添加文档")
            return
    
    print("\n=== 测试问答功能 ===")
    
    test_questions = [
        "什么是自然语言处理？",
        "Transformer模型的主要特点是什么？",
        "预训练语言模型有哪些应用？",
        "词向量的作用是什么？",
        "BERT模型和GPT模型有什么区别？",
        "量子计算的基本原理是什么？",
        "如何制作蛋糕？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        try:
            answer = simple_rag_query(vectordb, question)
            print(f"回答: {answer}")
        except Exception as e:
            print(f"回答: 文档中未找到相关答案")
            print(f"错误: {e}")
    
    print("\n=== 交互式问答 ===")
    while True:
        question = input("\n请输入问题（输入'q'退出）: ")
        if question.lower() == 'q':
            break
        if not question.strip():
            continue
        
        try:
            answer = simple_rag_query(vectordb, question)
            print(f"回答: {answer}")
        except Exception as e:
            print(f"回答: 文档中未找到相关答案")
            print(f"错误: {e}")

if __name__ == "__main__":
    main()