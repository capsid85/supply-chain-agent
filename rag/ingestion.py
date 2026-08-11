import os
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

def ingest_documents(file_paths: list, index_name: str = "supply-chain-kb"):
    """
    Ingest supplier docs, shipping route data, and historical events
    into Pinecone vector store if keys are present. Otherwise, log it.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")

    if not openai_key or not pinecone_key:
        print("API keys missing. Documents will be processed directly from CSV file inputs at query time.")
        return None

    all_docs = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"File {path} does not exist. Skipping.")
            continue
        if path.endswith('.pdf'):
            loader = PyPDFLoader(path)
        elif path.endswith('.csv'):
            loader = CSVLoader(path)
        else:
            continue
        docs = loader.load()
        all_docs.extend(docs)
    
    if not all_docs:
        print("No documents found to ingest.")
        return None

    # Chunk documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(all_docs)
    
    # Add metadata
    for chunk in chunks:
        chunk.metadata['ingested_at'] = datetime.utcnow().isoformat()
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = PineconeVectorStore.from_documents(
            chunks,
            embeddings,
            index_name=index_name
        )
        print(f"Ingested {len(chunks)} chunks into Pinecone index '{index_name}' successfully.")
        return vectorstore
    except Exception as e:
        print(f"Failed to ingest to Pinecone: {e}. Falling back to file-based query resolution.")
        return None
