import os
import re
import pickle

def load_pdf(file_path):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"读取PDF失败: {e}")
        return ""

def load_docx(file_path):
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"读取DOCX失败: {e}")
        return ""

def load_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"读取TXT失败: {e}")
        return ""

def load_document(file_path):
    _, ext = os.path.splitext(file_path.lower())
    if ext == '.pdf':
        return load_pdf(file_path)
    elif ext == '.docx':
        return load_docx(file_path)
    elif ext == '.txt':
        return load_txt(file_path)
    else:
        print(f"不支持的文件格式: {ext}")
        return ""

def load_documents_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            text = load_document(file_path)
            if text.strip():
                documents.append((filename, text))
    return documents

def split_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    text = text.strip()
    if not text:
        return chunks
    
    sentences = re.split(r'(?<=[。！？；.!?;])\s*', text)
    
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence[:chunk_size]
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    if not chunks:
        chunks.append(text[:chunk_size])
    
    if chunk_overlap > 0 and len(chunks) > 1:
        new_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0 and len(chunk) > chunk_overlap:
                chunk = chunks[i-1][-chunk_overlap:] + chunk
            new_chunks.append(chunk)
        chunks = new_chunks
    
    return chunks

def create_vector_db(documents, persist_directory="./vector_db"):
    try:
        import faiss
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        print(f"开始处理 {len(documents)} 个文档")
        
        all_chunks = []
        all_metadata = []
        
        for filename, content in documents:
            chunks = split_text(content, chunk_size=500, chunk_overlap=100)
            print(f"文件 {filename} 分割为 {len(chunks)} 个块")
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({"source": filename, "chunk_index": i})
        
        print(f"总共生成 {len(all_chunks)} 个文本块")
        
        if not all_chunks:
            print("错误: 没有有效的文本块")
            return None
        
        if len(all_chunks) < 1:
            print("错误: 文本块数量不足")
            return None
        
        vectorizer = TfidfVectorizer(max_features=min(384, max(10, len(all_chunks) * 10)), min_df=1)
        
        embeddings = vectorizer.fit_transform(all_chunks).toarray()
        print(f"向量维度: {embeddings.shape}")
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))
        
        os.makedirs(persist_directory, exist_ok=True)
        
        faiss.write_index(index, os.path.join(persist_directory, "index.faiss"))
        
        with open(os.path.join(persist_directory, "vectorizer.pkl"), 'wb') as f:
            pickle.dump(vectorizer, f)
        
        with open(os.path.join(persist_directory, "metadata.pkl"), 'wb') as f:
            pickle.dump(all_metadata, f)
        
        with open(os.path.join(persist_directory, "documents.pkl"), 'wb') as f:
            pickle.dump(all_chunks, f)
        
        print("向量数据库创建成功")
        return {"index": index, "vectorizer": vectorizer, "metadata": all_metadata, "documents": all_chunks}
    
    except Exception as e:
        print(f"创建向量数据库失败: {e}")
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        return None

def load_vector_db(persist_directory="./vector_db"):
    try:
        import faiss
        
        if not os.path.exists(persist_directory):
            return None
        
        index = faiss.read_index(os.path.join(persist_directory, "index.faiss"))
        
        with open(os.path.join(persist_directory, "vectorizer.pkl"), 'rb') as f:
            vectorizer = pickle.load(f)
        
        with open(os.path.join(persist_directory, "metadata.pkl"), 'rb') as f:
            metadata = pickle.load(f)
        
        with open(os.path.join(persist_directory, "documents.pkl"), 'rb') as f:
            documents = pickle.load(f)
        
        return {"index": index, "vectorizer": vectorizer, "metadata": metadata, "documents": documents}
    
    except Exception as e:
        print(f"加载向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def search_similar(db, query, k=3):
    try:
        import numpy as np
        
        query_embedding = db["vectorizer"].transform([query]).toarray().astype('float32')
        
        distances, indices = db["index"].search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append({
                    "document": db["documents"][idx],
                    "metadata": db["metadata"][idx],
                    "distance": float(distances[0][i])
                })
        
        return results
    except Exception as e:
        print(f"搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_documents_count(db):
    if db is None:
        return 0
    if isinstance(db, dict):
        return len(db.get("documents", []))
    return 0