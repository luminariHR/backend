from celery import shared_task
from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from supabase.client import create_client
from .models import ChatbotDocument
from core.vectorstores import VectorDBConnectionManager
import logging

logger = logging.getLogger(__name__)

connection_manager = VectorDBConnectionManager()


@shared_task
def store_doc_to_vectorstore(document_id):
    document = ChatbotDocument.objects.get(id=document_id)
    filepath = document.file.path
    loader = PyMuPDFLoader(filepath)
    docs = loader.load()
    for i, doc in enumerate(docs):
        doc.metadata["document_id"] = str(document_id)
        doc.metadata["source"] = filepath
        doc.metadata["category"] = document.category
        doc.metadata["page"] = i + 1

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_documents = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small",
    )
    supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )
    vector_store = connection_manager.get_connection(
        db_name="postgres",
        client=supabase_client,
        embeddings=embeddings,
    )
    vector_store.add_documents(split_documents)
