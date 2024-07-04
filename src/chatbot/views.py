from django.shortcuts import render
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChatbotDocument
from .serializers import ChatbotDocumentSerializer
from rest_framework.permissions import IsAdminUser
import os
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.response import Response
from .utils import extract_text_from_document
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from rest_framework import status


class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        user_message = request.data.get("user_message")
        if not user_message:
            return Response(
                {"error": "User message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 여기에서 챗봇 응답을 생성
        bot_response = "응답"

        # 메시지를 데이터베이스에 저장
        chatbot_message = Message.objects.create(
            question=user_message, answer=bot_response
        )
        serializer = MessageSerializer(chatbot_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def generate_bot_response(self, user_message):
        # 여기에 챗봇 응답 생성 로직을 추가
        # 예를 들어, 간단한 에코 응답을 반환
        return f"Echo: {user_message}"


class ChatbotDocumentList(generics.ListCreateAPIView):  # api
    queryset = ChatbotDocument.objects.all()
    serializer_class = ChatbotDocumentSerializer

    def post(self, request, *args, **kwargs):

        if request.method == "POST":
            title = request.POST["title"]
            file = request.FILES["file"]

            # 파일을 저장하고 파일 경로를 가져옵니다
            file_name = default_storage.save(file.name, file)
            file_path = default_storage.url(file_name)

            # 파일 객체를 데이터베이스에 저장
            chatbot_file = ChatbotDocument.objects.create(
                title=title, file_path=file_path
            )
            # 추출된 텍스트를 저장

            # 파일 업로드 후 바로 텍스트를 추출
            text = extract_text_from_document(settings.MEDIA_ROOT + file_path)
            print(text)  # 텍스트를 출력하거나 다른 작업을 수행

            return redirect("file-list")  # 파일 목록 페이지로 리다이렉트 html 이름

        return render(request, "chatbot/upload.html")  # 예시


class UploadFileView(APIView):  # html
    def get(self, request):
        return render(request, "chatbot/upload.html")

    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        file = request.FILES.get("file")

        if not title or not file:
            return render(
                request,
                "chatbot/upload.html",
                {"error": "Title and file are required."},
            )

        # 파일을 저장하고 파일 경로를 가져옵니다
        file_name = default_storage.save(file.name, file)
        file_path = default_storage.url(file_name)

        # 파일 객체를 데이터베이스에 저장
        chatbot_document = ChatbotDocument.objects.create(title=title, file=file_name)

        # 파일 업로드 후 바로 텍스트를 추출
        text = extract_text_from_document(os.path.join(settings.MEDIA_ROOT, file_path))

        # 추출된 텍스트를 저장

        return redirect("file-list")  # 파일 목록 페이지로 리다이렉트


class ChatbotDocumentDetail(generics.DestroyAPIView):
    queryset = ChatbotDocument.objects.all()
    serializer_class = ChatbotDocumentSerializer
