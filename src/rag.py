from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

class RAG:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.texts = []
        self.metadata = []
        self.index = None

    def extract_article(self, text):
        import re
        match = re.search(r'Article \d+.*?of CRR', text)
        return match.group(0) if match else "N/A"
    
    def load_docs(self, file_paths):

        for file_path in file_paths:
            with open(file_path, 'r') as f:
                content = f.read()
                chunks = content.split('\n\n')
            
            for chunk in chunks:
                if chunk.strip():
                    self.texts.append(chunk.strip())
                    self.metadata.append({'source': file_path, 'article': self.extract_article(chunk)})
        
        embeddings = self.model.encode(self.texts)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
    
    def save_index(self, index_path = 'data/processed/vector_index.faiss',metadata_path = 'data/processed/metadata.pkl'):
        os.makedirs(os.path.dirname(index_path), exist_ok = True)
        faiss.write_index(self.index, index_path)

        data = {
            'texts':self.texts,
            'metadata':self.metadata
        }

        with open(metadata_path, 'wb') as f:
            pickle.dump(data, f)

    def load_index(self, index_path='data/processed/vector_index.faiss',metadata_path= 'data/processed/metatdata.pkl'):
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(
                f"Index file not found. Please run load_doc() and save_index() first."
            )
        
        self.index = faiss.read_index(index_path)
        print(f"faiss index loaded for {index_path}")

        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
        self.texts = data['texts']
        self.metadata = data['metadata']
        print(f"loaded {len(self.texts)} text chunks for {metadata_path}")
    
    def Search(self, query, top_k=2):

        if self.index is None:
            raise ValueError("Index not found. call load_docs() or load_index() function first.")

        query_embeddings = self.model.encode([query])
        query_embeddings = np.array(query_embeddings).astype('float32')

        distances, indices = self.index.search(query_embeddings, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'paragraph_id': str(idx),
                'text' : self.texts[idx],
                'source': self.metadata[idx]['source'],
                'article': self.metadata[idx]['article'],
                'relevance_score': 1 / (1 + float(distances[0][i]))
            })

        return results

# if __name__ == "__main__":
#     rag = RAG()
#     rag.load_docs([
#         'data/rag_text/c01_instructions.txt.txt',
#         'data/rag_text/c02_instructions.txt.txt',
#         'data/rag_text/c01_validation_rules.txt.txt',
#         'data/rag_text/c02_validation_rules.txt.txt'
#     ])
#     rag.save_index()

#     results = rag.Search("What is the artical 26 is about?")
#     for r in results:
#         print(r['text'])