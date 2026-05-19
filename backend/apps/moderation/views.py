from rest_framework import generics, status
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from .models import Ban
from .serializers import BanSerializer
from .services import ban_user, unban_user


class BanListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class   = BanSerializer
    queryset           = Ban.objects.filter(is_active=True).select_related(
        'user', 'banned_by', 'unbanned_by'
    )
    search_fields  = ['user__email', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target          = serializer.validated_data['user']
        reason          = serializer.validated_data['reason']
        trigger_message = serializer.validated_data.get('trigger_message', '')

        ban = ban_user(target, request.user, reason, trigger_message)
        return Response(BanSerializer(ban).data, status=status.HTTP_201_CREATED)


class BanDestroyView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class   = BanSerializer
    queryset           = Ban.objects.filter(is_active=True).select_related('user', 'banned_by')
    lookup_field       = 'pk'

    def perform_destroy(self, instance):
        unban_user(instance, self.request.user)
