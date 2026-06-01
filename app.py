import streamlit as st
import os
import tempfile
from utils import load_document, create_vector_db, load_vector_db, get_documents_count
from rag_chain import simple_rag_query

st.set_page_config(page_title="RAG智能问答系统", page_icon="🤖", layout="wide")

def init_session_state():
    if 'vectordb' not in st.session_state:
        st.session_state.vectordb = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False
    if 'document_count' not in st.session_state:
        st.session_state.document_count = 0

init_session_state()

st.title("📚 RAG智能问答系统")
st.markdown("基于本地知识库的智能问答助手")

col1, col2 = st.columns([1, 2.5], gap="large")

with col1:
    st.subheader("📁 知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="支持PDF、DOCX和TXT格式的文档"
    )
    
    if uploaded_files:
        st.write("已上传文件:")
        for uploaded_file in uploaded_files:
            st.write(f"- {uploaded_file.name} ({round(uploaded_file.size / 1024, 1)} KB)")
    
    col_btn1, col_btn2 = st.columns(2, gap="small")
    with col_btn1:
        build_btn = st.button("构建知识库", use_container_width=True)
    with col_btn2:
        load_btn = st.button("加载知识库", use_container_width=True)
    
    if build_btn and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            documents = []
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"正在读取文件: {uploaded_file.name}")
                progress_bar.progress((i + 1) / (total_files + 2))
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                text = load_document(tmp_path)
                os.unlink(tmp_path)
                
                if text.strip():
                    documents.append((uploaded_file.name, text))
                    st.write(f"✅ {uploaded_file.name}: 读取到 {len(text)} 个字符")
                else:
                    st.write(f"⚠️ {uploaded_file.name}: 未读取到有效内容")
            
            if not documents:
                st.error("❌ 未找到有效文档内容，请检查文件格式")
            else:
                status_text.text("正在创建向量数据库...")
                progress_bar.progress((total_files + 1) / (total_files + 2))
                
                vectordb = create_vector_db(documents, "./vector_db")
                
                if vectordb:
                    st.session_state.vectordb = vectordb
                    st.session_state.document_count = get_documents_count(vectordb)
                    st.session_state.db_initialized = True
                    progress_bar.progress(1.0)
                    status_text.text("")
                    st.success(f"✅ 知识库构建完成！共处理 {len(documents)} 个文档，生成 {st.session_state.document_count} 个文本块")
                else:
                    st.error("❌ 创建向量数据库失败，请检查控制台输出获取详细信息")
        except Exception as e:
            st.error(f"❌ 处理过程中发生错误: {str(e)}")
            import traceback
            st.text(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("快速体验")
    if st.button("使用示例文档构建知识库", use_container_width=True):
        with st.spinner("正在加载示例文档..."):
            try:
                from utils import load_documents_from_folder
                sample_docs = load_documents_from_folder("./自然语言处理")
                
                if sample_docs:
                    st.write(f"找到 {len(sample_docs)} 个示例文档")
                    vectordb = create_vector_db(sample_docs, "./vector_db")
                    
                    if vectordb:
                        st.session_state.vectordb = vectordb
                        st.session_state.document_count = get_documents_count(vectordb)
                        st.session_state.db_initialized = True
                        st.success(f"✅ 示例知识库构建完成！共 {st.session_state.document_count} 个文本块")
                    else:
                        st.error("❌ 创建示例知识库失败")
                else:
                    st.warning("⚠️ 未找到示例文档")
            except Exception as e:
                st.error(f"❌ 加载示例文档失败: {str(e)}")
    elif build_btn and not uploaded_files:
        st.warning("⚠️ 请先上传文档")
    
    if load_btn:
        with st.spinner("正在加载知识库..."):
            vectordb = load_vector_db("./vector_db")
            if vectordb:
                st.session_state.vectordb = vectordb
                st.session_state.document_count = get_documents_count(vectordb)
                st.session_state.db_initialized = True
                st.success(f"✅ 知识库加载成功！共 {st.session_state.document_count} 个文本块")
            else:
                st.warning("⚠️ 未找到现有知识库")
    
    st.markdown("---")
    status_text = "已连接" if st.session_state.db_initialized else "未连接"
    st.write(f"**知识库状态**: {'🟢' if st.session_state.db_initialized else '🔴'} {status_text}")
    st.write(f"**文本块数量**: {st.session_state.document_count}")
    st.write(f"**对话历史**: {len(st.session_state.chat_history)} 条")
    
    if st.session_state.chat_history:
        if st.button("清空对话历史", use_container_width=True):
            st.session_state.chat_history = []
            st.success("对话历史已清空")

with col2:
    st.subheader("💬 问答交互")
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for role, content in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"""
                    <div style="background: #e8f5e9; border-radius: 16px; padding: 12px 16px; margin-bottom: 8px;">
                        <div style="font-weight: 600; color: #2e7d32; margin-bottom: 4px;">您</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f5f5f5; border-radius: 16px; padding: 12px 16px; margin-bottom: 8px;">
                        <div style="font-weight: 600; color: #546e7a; margin-bottom: 4px;">助手</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            ready_text = "" if st.session_state.db_initialized else "未"
            hint_text = "请输入问题开始对话" if st.session_state.db_initialized else "请先构建或加载知识库"
            st.markdown(f"""
            <div style="text-align: center; padding: 60px 20px; color: #64748b;">
                <div style="font-size: 48px; margin-bottom: 16px;">🤖</div>
                <div>知识库{ready_text}就绪</div>
                <div style="font-size: 14px; margin-top: 8px; color: #94a3b8;">{hint_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    input_col, btn_col = st.columns([5, 1], gap="medium")
    with input_col:
        question = st.text_input(
            "请输入您的问题...",
            key="question",
            disabled=not st.session_state.db_initialized
        )
    with btn_col:
        submit_btn = st.button(
            "发送",
            key="submit",
            use_container_width=True,
            disabled=not st.session_state.db_initialized or not question.strip()
        )
    
    if submit_btn and question.strip() and st.session_state.db_initialized:
        st.session_state.chat_history.append(("user", question))
        
        with st.spinner("正在思考..."):
            answer = simple_rag_query(st.session_state.vectordb, question)
            st.session_state.chat_history.append(("assistant", answer))
        
        st.rerun()
    
    st.markdown("""
    <div style="margin-top: 16px; padding: 12px 16px; background: rgba(34, 197, 94, 0.05); border-radius: 8px; border: 1px solid rgba(34, 197, 94, 0.15);">
        <div style="display: flex; align-items: center; gap: 8px; color: #16a34a; font-size: 13px;">
            <span>💡</span>
            <span>提示：基于文档内容回答，若文档中没有相关信息将明确说明</span>
        </div>
    </div>
    """, unsafe_allow_html=True)