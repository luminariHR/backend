from .serializers import AdminAppointmentSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from core.permissions import IsHRAdmin


class AdminAppointmentView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        context = {"request": request}
        serializer = AdminAppointmentSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 인사 발령이 되었습니다.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=400)
