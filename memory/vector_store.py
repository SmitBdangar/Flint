import os
from pathlib import Path
from typing import List, Dict, Any

try:
    import chromadb
    import tiktoken
except ImportError:
    chromadb = None
    tiktoken = None

class VectorStore:
    def __init__(self, db_path: str = "~/.flint/vector_db", collection_name: str = "codebase"):
        if chromadb is None or tiktoken is None:
            raise ImportError("Please install chromadb and tiktoken to use Vector Memory.")
            
        db_path = os.path.expanduser(db_path)
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Tokenizer for chunking text
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = 500
        self.chunk_overlap = 50

    def chunk_text(self, text: str) -> List[str]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunks.append(self.tokenizer.decode(chunk_tokens))
            
        return chunks

    def index_directory(self, dir_path: str, extensions: List[str] = None):
        """Recursively index all text files matching the extensions."""
        if extensions is None:
            extensions = [".py", ".md", ".txt", ".js", ".ts", ".html", ".css", ".json", ".rs", ".go"]
            
        dir_path = Path(dir_path).resolve()
        
        docs = []
        metadatas = []
        ids = []
        
        print(f"Indexing directory: {dir_path}")
        
        for root, _, files in os.walk(dir_path):
            # Skip hidden directories like .git
            if any(part.startswith('.') for part in Path(root).parts):
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        chunks = self.chunk_text(content)
                        rel_path = os.path.relpath(file_path, dir_path)
                        
                        for i, chunk in enumerate(chunks):
                            docs.append(chunk)
                            metadatas.append({"file": rel_path, "chunk_index": i})
                            ids.append(f"{rel_path}_{i}")
                            
                    except Exception as e:
                        # Skip files that can't be read (e.g. binary disguised as text)
                        pass
                        
        if docs:
            # Batch upsert to chroma
            batch_size = 100
            for i in range(0, len(docs), batch_size):
                self.collection.upsert(
                    documents=docs[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )
            print(f"Successfully indexed {len(docs)} chunks from '{dir_path.name}'.")
        else:
            print("No valid text files found to index.")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search the indexed codebase."""
        if not self.collection.count():
            print("Vector store is empty. Please run `flint memory index` first.")
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        formatted_results = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            for idx in range(len(results["documents"][0])):
                formatted_results.append({
                    "id": results["ids"][0][idx],
                    "document": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx] if results["metadatas"] else {}
                })
                
        return formatted_results
