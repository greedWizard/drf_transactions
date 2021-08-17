from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from balances.serializers import CreditPostSerializer, CreditReadSerializer, DebitPostSerializer, DebitReadSerializer, TransferPostSerializer, TransferReadSerializer

from balances.services import OperationService
from users.serializers import UserWithHistorySerializer
from users.services import UserService


class OperationView(ViewSet):
    service = OperationService
    debit_action_serializer = DebitPostSerializer
    credit_action_serializer = CreditPostSerializer
    transfer_action_serializer = TransferPostSerializer

    debit_read_serializer = DebitReadSerializer
    credit_read_serializer = CreditReadSerializer
    transfer_read_serializer = TransferReadSerializer

    user_history_serializer = UserWithHistorySerializer

    user_service = UserService

    @action(methods=['POST'], detail=False)
    def debit(self, request: Request):
        action_serializer = self.debit_action_serializer(data=request.data)

        if action_serializer.is_valid(raise_exception=True):
            debit = self.service().debit(
                **action_serializer.data,
            )
            read_serializer = self.debit_read_serializer(debit, many=False)

            return Response(
                read_serializer.data
            )

    @action(methods=['POST'], detail=False)
    def credit(self, request: Request):
        action_serializer = self.credit_action_serializer(data=request.data)

        if action_serializer.is_valid(raise_exception=True):
            credit = self.service().credit(
                **action_serializer.data,
            )
            read_serializer = self.credit_read_serializer(credit, many=False)

            return Response(
                read_serializer.data
            )

    @action(methods=['POST'], detail=False)
    def transfer(self, request: Request):
        action_serializer = self.transfer_action_serializer(data=request.data)

        if action_serializer.is_valid(raise_exception=True):
            transfer = self.service().transfer(
                **action_serializer.data,
            )
            read_serializer = self.transfer_read_serializer(transfer, many=False)

            return Response(
                read_serializer.data
            )

    @action(methods=['GET'], detail=False)
    def history(self, request: Request):
        print(request.query_params)
        pk = request.query_params['user_id']

        user = self.user_service().retrieve(pk)

        serializer = UserWithHistorySerializer(user, many=False)

        return Response(
            data=serializer.data,
        )

        