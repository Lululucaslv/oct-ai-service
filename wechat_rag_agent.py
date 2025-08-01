import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import chromadb
from pathlib import Path

load_dotenv()

logger = logging.getLogger(__name__)

class WeChatRAGAgent:
    def __init__(self):
        self.knowledge_base_path = "/app/knowledge_base"
        self.vector_store_path = "/app/vector_store"
        self.llm = None
        self.vector_store = None
        self.embeddings = None
        self.conversation_history = {}
        
        self._initialize_llm()
        self._initialize_knowledge_base()
    
    def _initialize_llm(self):
        """Initialize Gemini LLM"""
        try:
            gemini_api_key = os.getenv('GOOGLE_API_KEY')
            if not gemini_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            genai.configure(api_key=gemini_api_key)
            self.llm = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info("Gemini LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise HTTPException(status_code=500, detail=f"LLM initialization failed: {e}")
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base and vector store"""
        try:
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            if self._vector_store_exists():
                logger.info("Loading existing vector store")
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Creating new vector store from knowledge base")
                self._create_vector_store()
            
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            raise HTTPException(status_code=500, detail=f"Knowledge base initialization failed: {e}")
    
    def _vector_store_exists(self) -> bool:
        """Check if vector store already exists"""
        return os.path.exists(os.path.join(self.vector_store_path, "chroma.sqlite3"))
    
    def _create_vector_store(self):
        """Create vector store from knowledge base documents"""
        try:
            if not os.path.exists(self.knowledge_base_path):
                logger.warning(f"Knowledge base path {self.knowledge_base_path} does not exist")
                return
            
            loader = DirectoryLoader(
                self.knowledge_base_path,
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                logger.warning("No documents found in knowledge base")
                return
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            texts = text_splitter.split_documents(documents)
            
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=self.vector_store_path
            )
            
            self.vector_store.persist()
            logger.info(f"Created vector store with {len(texts)} document chunks")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise e
    
    def _retrieve_relevant_docs(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant documents from vector store"""
        try:
            if not self.vector_store:
                return []
            
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _get_conversation_context(self, user_id: str, max_turns: int = 3) -> str:
        """Get recent conversation context for user"""
        if user_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[user_id]
        recent_history = history[-max_turns*2:] if len(history) > max_turns*2 else history
        
        context = ""
        for i in range(0, len(recent_history), 2):
            if i+1 < len(recent_history):
                context += f"用户: {recent_history[i]}\n助手: {recent_history[i+1]}\n\n"
        
        return context
    
    def _update_conversation_history(self, user_id: str, user_message: str, assistant_response: str):
        """Update conversation history for user"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].extend([user_message, assistant_response])
        
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return """你是"归芯"项目的专业技术客服助手。你的主要职责是：

1. 回答用户关于开源硬件（如Arduino、Raspberry Pi等）的技术问题
2. 提供准确、专业的技术指导和解决方案
3. 基于提供的技术文档和知识库回答问题
4. 保持友好、耐心的服务态度

回答要求：
- 使用中文回答
- 回答要准确、专业、易懂
- 如果问题超出知识范围，诚实说明并建议联系技术专家
- 提供具体的代码示例或操作步骤（如适用）
- 保持回答简洁但完整

当前对话上下文会帮助你更好地理解用户的连续问题。"""

    async def process_message(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process user message and generate response"""
        try:
            relevant_docs = self._retrieve_relevant_docs(user_message)
            conversation_context = self._get_conversation_context(user_id)
            
            context_text = ""
            if relevant_docs:
                context_text = "\n\n相关技术文档:\n" + "\n---\n".join(relevant_docs)
            
            conversation_text = ""
            if conversation_context:
                conversation_text = f"\n\n最近对话历史:\n{conversation_context}"
            
            prompt = f"""{self._get_system_prompt()}

{conversation_text}

{context_text}

用户问题: {user_message}

请基于上述技术文档和对话历史，为用户提供专业的技术支持回答："""

            response = self.llm.generate_content(prompt)
            assistant_response = response.text.strip()
            
            self._update_conversation_history(user_id, user_message, assistant_response)
            
            return {
                "user_message": user_message,
                "assistant_response": assistant_response,
                "relevant_docs_count": len(relevant_docs),
                "user_id": user_id,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = "抱歉，处理您的问题时出现技术故障。请稍后重试或联系技术支持。"
            return {
                "user_message": user_message,
                "assistant_response": error_response,
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get knowledge base information"""
        try:
            info = {
                "knowledge_base_path": self.knowledge_base_path,
                "vector_store_path": self.vector_store_path,
                "vector_store_exists": self._vector_store_exists(),
                "status": "success"
            }
            
            if self.vector_store:
                try:
                    collection = self.vector_store._collection
                    info["document_count"] = collection.count()
                except:
                    info["document_count"] = "unknown"
            
            knowledge_files = []
            if os.path.exists(self.knowledge_base_path):
                for file_path in Path(self.knowledge_base_path).rglob("*.md"):
                    knowledge_files.append(str(file_path.relative_to(self.knowledge_base_path)))
            
            info["knowledge_files"] = knowledge_files
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting knowledge base info: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def clear_conversation_history(self, user_id: str = None):
        """Clear conversation history for specific user or all users"""
        if user_id:
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
                logger.info(f"Cleared conversation history for user: {user_id}")
        else:
            self.conversation_history.clear()
            logger.info("Cleared all conversation history")

wechat_rag_agent = None

def get_wechat_rag_agent() -> WeChatRAGAgent:
    """Get or create WeChat RAG agent instance"""
    global wechat_rag_agent
    if wechat_rag_agent is None:
        wechat_rag_agent = WeChatRAGAgent()
    return wechat_rag_agent

async def test_rag_agent():
    """Test the RAG agent with sample questions"""
    agent = get_wechat_rag_agent()
    
    test_questions = [
        "Arduino Uno有多少个数字引脚？",
        "Raspberry Pi 4的处理器是什么？",
        "如何在Arduino上控制LED闪烁？",
        "Raspberry Pi的GPIO引脚电压是多少？"
    ]
    
    results = []
    for i, question in enumerate(test_questions, 1):
        print(f"\n=== 测试问题 {i} ===")
        print(f"问题: {question}")
        
        result = await agent.process_message(question, f"test_user_{i}")
        results.append(result)
        
        print(f"回答: {result['assistant_response']}")
        print(f"相关文档数量: {result['relevant_docs_count']}")
        print(f"状态: {result['status']}")
        print("-" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(test_rag_agent())
