from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from django.http.response import JsonResponse
from .serializers import UserSerializer
from .models import User
import jwt, datetime

# Create your views here.
class RegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({'message': 'Successful Registration', 'account': serializer.data}, status=status.HTTP_204_NO_CONTENT)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    @csrf_exempt
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        
        user = User.objects.filter(username=username).first()
        
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Password is wrong!')
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        
        return response
    

class UserView(APIView):
    @csrf_exempt
    def get(self, request):
        token = request.COOKIES.get('jwt')
        
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    
class LogoutView(APIView):
    @csrf_exempt
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'Logout Success'}
        
        return response