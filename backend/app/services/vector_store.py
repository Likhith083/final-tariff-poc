import chromadb
import json
import os
from typing import List, Dict, Any, Optional
from app.core.config import settings

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection_name = "tariff_knowledge"
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Tariff AI Knowledge Base"}
            )
    
    async def load_knowledge_base(self, knowledge_base_path: str) -> int:
        """Load knowledge base from JSON file"""
        if not os.path.exists(knowledge_base_path):
            raise FileNotFoundError(f"Knowledge base file not found: {knowledge_base_path}")
        
        try:
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            # Process FAQ data
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        # Handle different data structures
                        if 'question' in item and 'answer' in item:
                            content = f"Q: {item['question']}\nA: {item['answer']}"
                            documents.append(content)
                            metadatas.append({
                                "type": "faq",
                                "category": item.get("category", "general"),
                                "source": "adcvd_faq"
                            })
                            ids.append(f"faq_{i}")
                        elif 'title' in item and 'content' in item:
                            content = f"{item['title']}\n{item['content']}"
                            documents.append(content)
                            metadatas.append({
                                "type": "article",
                                "category": item.get("category", "general"),
                                "source": "knowledge_base"
                            })
                            ids.append(f"article_{i}")
            
            # Add to vector store
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            return len(documents)
            
        except Exception as e:
            raise Exception(f"Failed to load knowledge base: {str(e)}")
    
    async def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Vector search error: {str(e)}")
            return []
    
    async def add_document(self, content: str, metadata: Dict[str, Any], doc_id: str):
        """Add a single document to the knowledge base"""
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"Failed to add document: {str(e)}")
            return False
    
    async def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Update an existing document"""
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            print(f"Failed to update document: {str(e)}")
            return False
    
    async def delete_document(self, doc_id: str):
        """Delete a document from the knowledge base"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Failed to delete document: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_function": "default"
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0
            }
    
    async def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._get_or_create_collection()
            return True
        except Exception as e:
            print(f"Failed to clear collection: {str(e)}")
            return False 