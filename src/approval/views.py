import io
from PIL import Image
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Approval, Agenda
from .serializers import (
    ApprovalSerializer,
    AgendaReviewRequestCreateSerializer,
    AgendaSerializer,
    AgendaReviewSerializer,
    OCRSerializer,
)
from .ocr import ReceiptParser


class SentApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Approval.objects.filter(requester=user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class ReviewApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Approval.objects.filter(approver=user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        status_update = request.data.get("status")

        if status_update not in ["approved", "rejected", "pending"]:
            return Response(
                {"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = status_update
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AgendaReviewRequestCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, version):
        context = {"request": request}
        serializer = AgendaReviewRequestCreateSerializer(
            data=request.data, context=context
        )
        if serializer.is_valid():
            approval_request = serializer.save()
            response_serializer = AgendaSerializer(
                approval_request,
                context=context,
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgendaReviewView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, version, agenda_id):
        context = {"request": request}
        try:
            agenda = Agenda.objects.get(id=agenda_id)
        except Agenda.DoesNotExist:
            return Response(
                {"message": "처리할 수 없는 결재입니다."},
                status=404,
            )
        serializer = AgendaReviewSerializer(agenda, data=request.data, context=context)
        if serializer.is_valid():
            approval_request = serializer.save()
            response_serializer = AgendaSerializer(approval_request, context=context)
            return Response(
                {
                    "message": "성공적으로 반영됐습니다.",
                    "data": response_serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class SentReviewRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        context = {"request": request}

        drafter = request.user
        if start_date and end_date:
            agendas = Agenda.objects.filter(
                drafter=drafter,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
            )
        else:
            agendas = Agenda.objects.filter(drafter=drafter)
        response_serializer = AgendaSerializer(agendas, context=context, many=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReceivedReviewRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        reviewer = request.user
        if start_date and end_date:
            agendas = Agenda.objects.filter(
                review_steps__reviewer=reviewer,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
            )
        else:
            agendas = Agenda.objects.filter(review_steps__reviewer=reviewer)
        agendas = agendas.exclude(review_steps__status="standby").distinct()
        response_serializer = AgendaSerializer(agendas, context=context, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReferencedReviewRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        referrer = request.user
        if start_date and end_date:
            agendas = Agenda.objects.filter(
                references__referrer=referrer,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
            ).distinct()
        else:
            agendas = Agenda.objects.filter(references__referrer=referrer).distinct()
        response_serializer = AgendaSerializer(agendas, context=context, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class OCRView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OCRSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["image"]
            try:
                image = Image.open(io.BytesIO(file.read()))
                parser = ReceiptParser(image)
                response = parser.parse()
                return Response({"preview": response}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
