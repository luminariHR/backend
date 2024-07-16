from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from supabase.client import create_client
from core.permissions import IsHRAdmin
from .models import ChatbotMessage, ChatbotDocument
from .serializers import MessageSerializer, ChatbotDocumentSerializer
from .vectorstores import VectorDBConnectionManager
from .utils import answer_question_based_on_metadata

connection_manager = VectorDBConnectionManager()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = ChatbotMessage.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatbotMessage.objects.filter(author=user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_create(self, serializer):
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
        retriever = vector_store.as_retriever(
            search_kwargs={"filter": {"category": self.request.data["category"]}}
        )
        response = answer_question_based_on_metadata(
            retriever, self.request.data["question"]
        )
        serializer.save(author=self.request.user, answer=response)


# HR 관리자 View
class AdminChatbotDocumentCreateView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        context = {"request": request}
        serializer = ChatbotDocumentSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 데이터가 생성되었습니다.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=400)

    def get(self, request, version, document_id=None):
        context = {"request": request}
        if document_id is None:
            documents = ChatbotDocument.objects.all()
            serializer = ChatbotDocumentSerializer(documents, many=True)
        else:
            document = ChatbotDocument.objects.filter(id=document_id).distinct()
            serializer = ChatbotDocumentSerializer(document)
        return Response(serializer.data)


class AdminChatbotDocumentView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, document_id):
        context = {"request": request}
        document = ChatbotDocument.objects.get(id=document_id)
        serializer = ChatbotDocumentSerializer(document)
        return Response(serializer.data)
