from celery import shared_task
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from supabase.client import create_client
from langchain.docstore.document import Document
from core.vectorstores import VectorDBConnectionManager
import logging

logger = logging.getLogger(__name__)

connection_manager = VectorDBConnectionManager()


@shared_task
def add_profiles_to_vector_store(content, employee_id):
    documents = [
        Document(
            page_content=content,
            metadata={"employee_id": employee_id, "category": "mentorship"},
        )
    ]
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-large",
    )
    supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )
    vector_store = connection_manager.get_connection(
        db_name="postgres_mentorship",
        client=supabase_client,
        embeddings=embeddings,
        table_name="mentorship_documents",
        query_name="mentorship_match_documents",
    )
    vector_store.add_documents(documents)
