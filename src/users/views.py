from rest_framework.permissions import AllowAny
from .serializers import UserPostSerializer, UserReadSerializer
from base.views import ServiceViewSet
from .services import UserService



class UserViewSet(ServiceViewSet):
    ''' Flat ViewSet '''
    service = UserService
    read_serializer = UserReadSerializer
    action_serializer = UserPostSerializer
    permission_classes = (AllowAny, )
