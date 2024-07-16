from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer

class AccountPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    pagination_class = AccountPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_queryset(self):
        queryset = Account.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    @action(detail=False, methods=['post'])
    def import_accounts(self, request):
        file = request.FILES['file']
        df = pd.read_csv(file)
        accounts = [Account(id=row['ID'], name=row['name'], balance=row['balance']) for _, row in df.iterrows()]
        Account.objects.bulk_create(accounts)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        from_account = self.get_object()
        to_account = Account.objects.get(id=request.data['to_account'])
        amount = request.data['amount']

        if from_account.balance >= amount:
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            transaction = Transaction(from_account=from_account, to_account=to_account, amount=amount)
            transaction.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
