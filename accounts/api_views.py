from rest_framework import viewsets
from .serializers import CustomUserSerializer
from .models import CustomUser
from django.db.models import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer    
from rest_framework.views import APIView

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        if self.action in [list, 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     token, created = Token.objects.get_or_create(user=serializer.instance)
    #     return Response({
    #         'token': token.key,
    #         'id': serializer.instance.id,
    #         'email': serializer.instance.email
    #     }, status=status.HTTP_201_CREATED, headers=headers)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)

class CustomAuthTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get the authentication token for the given user."""
        try:
            user = request.user
            token = Token.objects.get(user=user)
            response_data = {
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }
            return Response(response_data)
        except ObjectDoesNotExist:
            return Response("Token not found.", status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        """Create a new authentication token for the given user."""
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            try:
                token = Token.objects.get(user=user)
                response_data = {
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                }
                return Response(response_data)
            except ObjectDoesNotExist:
                token = Token.objects.create(user=user)
                response_data = {
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                }
                return Response(response_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Delete the authentication token for the given user."""
        try:
            user = request.user
            token = Token.objects.get(user=user)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response("Token not found.", status=status.HTTP_404_NOT_FOUND)
    