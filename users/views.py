from rest_framework import viewsets
from rest_framework.decorators import action


class AuthenticationViewSet(viewsets.ViewSet):
    @action(methods=['POST'], detail=False)
    def login(self, request):
        pass

    def register(self, request):
        pass
