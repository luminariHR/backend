import uuid
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
from core.vectorstores import VectorDBConnectionManager
from .utils import answer_question_based_on_metadata

connection_manager = VectorDBConnectionManager()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = ChatbotMessage.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatbotMessage.objects.filter(author=user)

    def filter_queryset(self, queryset):
        filter_value = self.request.query_params.get("category", None)
        if filter_value is not None:
            queryset = queryset.filter(category=filter_value)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_create(self, serializer):
        if settings.OPENAI_API_KEY:
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
        else:
            response = f"{self.request.data['question']}에 대한 답변입니다. API Key를 넣어주세요."
        serializer.save(author=self.request.user, answer=response)


class ChatbotDocumentListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        document = ChatbotDocument.objects.all()
        serializer = ChatbotDocumentSerializer(document, context=context, many=True)
        return Response(serializer.data)


class ChatbotDocumentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version, document_id):
        context = {"request": request}
        document = ChatbotDocument.objects.get(id=document_id)
        serializer = ChatbotDocumentSerializer(document, context=context)
        return Response(serializer.data)


# HR 관리자 View
class AdminChatbotDocumentCreateView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        context = {"request": request}
        data = {
            "name": request.data["name"],
            "description": request.data["description"],
            "category": request.data["category"],
            "id": uuid.uuid4(),
            "file": request.data["file"],
        }
        serializer = ChatbotDocumentSerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 데이터가 생성되었습니다.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=400)


class AdminChatbotDocumentView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, document_id):
        context = {"request": request}
        document = ChatbotDocument.objects.get(id=document_id)
        serializer = ChatbotDocumentSerializer(document, context=context)
        return Response(serializer.data)

    def delete(self, request, version, document_id):
        context = {"request": request}
        try:
            document = ChatbotDocument.objects.get(id=document_id)
        except ChatbotDocument.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 문서입니다."},
                status=404,
            )
        serializer = ChatbotDocumentSerializer(
            document, data=request.data, partial=True, context=context
        )
        serializer.delete(document)
        return Response({"message": "성공적으로 문서가 삭제됐습니다."}, status=200)
