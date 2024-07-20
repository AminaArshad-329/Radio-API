from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from users.serializers import LoginSerializer
from .models import User


class LoginView(APIView):
    """ Login functionality """
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        email = validated_data.get('email', None)
        password = validated_data.get('password', None)

        try:
            user = User.objects.filter(email=email, is_active=True).first()
        except Exception as ex:
            return Response({'error': f'Exception occurred {ex}'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            raise ValueError('User does not exist!')

        if not user.check_password(password):
            raise ValueError('Invalid password')

        token = AccessToken.for_user(user)
        return Response({'token': str(token)})
