from typing import List, Tuple, Type
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.serializers import Serializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .services import IService


# TODO: переписать AutoSchema чтобы автоматически подставлялись сериалайзеры в list, update, destroy и т.д.
# TODO: донастроить operation_id чтоб не было повторений, для этого настроить теги для целой вьюхи


class ServiceViewSetBase(ViewSet):
    service: Type[IService] = None
    read_serializer: Type[Serializer] = None


class ServiceViewSetRead(ServiceViewSetBase):
    def list(self, request: Request, *args, **kwargs):
        ''' получить список всех объектов '''
        filters = request.query_params
        objects = self.service().fetch(**filters)

        serializer = self.read_serializer(objects, many=True)

        return Response(
            data=serializer.data,
        )

    def retrieve(self, request: Request, pk=None, *args, **kwrags):
        ''' получить один конкретный объект '''
        object = self.service().retrieve(pk=pk)
        serializer = self.read_serializer(object, many=False)

        return Response(
            data=serializer.data,
        )


class ServiceViewSetAction(ServiceViewSetBase):
    action_serializer: Type[Serializer] = None

    def validate_action(
        self,
        request: Request,
        raise_exception=True,
    ) -> Tuple[Serializer, bool]:
        ''' проверить поля в серилазиаторе для записи '''
        action_sr = self.action_serializer(data=request.data)
        return action_sr, action_sr.is_valid(raise_exception=raise_exception)

    def update(self, request: Request, pk=None):
        ''' редактировать конкретный объект '''
        action_sr, valid = self.validate_action(request)

        if valid:
            data = action_sr.data
            object = self.service().update(action_sr.data, pk=pk).first()
            read_sr = self.read_serializer(object)

            return Response(
                read_sr.data
            )

    def create(self, request: Request):
        ''' создать новый объект '''
        action_sr, valid = self.validate_action(request)

        if valid:
            new_obj = self.service().create(**action_sr.data)
            read_sr = self.read_serializer(new_obj)

            return Response(
                read_sr.data
            )

    def destroy(self, request: Request, pk=None):
        ''' удалить один конкретный объект '''
        delete = self.service().delete(pk=pk)

        return Response(
            {
                'status': 'success'
            }
        )


    @action(methods=['post'], detail=False)
    def bulk_delete(self, request: Request):
        ''' удалить множество объектов сразу по переданным pk '''
        self.service().bulk_delete(*request.data.get('pks', []))

        return Response(
            {
                'status': 'success'
            }
        )


class ServiceViewSet(ServiceViewSetRead, ServiceViewSetAction):
    '''
        Вьюсеты для работы с сервисами. Все вьюхи должны быть реализованы через наследников
        данного класса, чтобы не протеворечить SOLID.
    '''
    permission_classes = (IsAuthenticated, )
