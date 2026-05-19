from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .serializers import SubscribeSerializer, UnsubscribeSerializer
from .services import send_welcome


class SubscribeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes   = [AnonRateThrottle]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscriber, created = serializer.save()
        # Welcome email — HTML + plain text via templates in services.py.
        # Failures are swallowed inside send_welcome so an SMTP outage
        # can't break the user-visible subscribe flow.
        send_welcome(subscriber)
        msg = 'Inscrição realizada com sucesso!' if created else 'E-mail já inscrito e reativado.'
        return Response({'detail': msg}, status=status.HTTP_200_OK)


class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Inscrição cancelada com sucesso.'}, status=status.HTTP_200_OK)
