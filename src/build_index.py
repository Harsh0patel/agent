from src.rag import RAG

print("Building vector index (one-time setup)...")

builder = RAG()

builder.load_docs([
    'C:/Users/hp333/Desktop/agent/data/rag_text/c01_instructions.txt.txt',
    'C:/Users/hp333/Desktop/agent/data/rag_text/c02_instructions.txt.txt',
    'C:/Users/hp333/Desktop/agent/data/rag_text/c01_validation_rules.txt.txt',
    'C:/Users/hp333/Desktop/agent/data/rag_text/c02_validation_rules.txt.txt'
])

builder.save_index(
    index_path = 'data/processed/vector_index.faiss',
    metadata_path = 'data/processed/metadata.pkl'
)

print("Index built and saved successfully!")
