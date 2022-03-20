from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import JSONParser 
import json
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from django.http.response import JsonResponse
from .serializers import UserSerializer, DeckSerializer
from .models import User, Decks
import jwt, datetime

# Create your views here.
class RegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        user = User.objects.filter(username=request.data['username']).first()
        usermail = User.objects.filter(email=request.data['email']).first()
        
        if user is not None:
            return JsonResponse({'message': 'Username already used'}, status=status.HTTP_400_BAD_REQUEST)
        
        if usermail is not None:
            return JsonResponse({'message': 'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({'message': 'Successful Registration', 'account': serializer.data}, status=status.HTTP_201_CREATED)
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
            'username': user.username,
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
        
        
        token = request.headers.get('jwt')
        
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        Author = User.objects.filter(username = payload['username'])
        
        if Author is None:
            return JsonResponse({'message': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
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
    
class DeckView(APIView):
    @csrf_exempt
    def get(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated! you need login first')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated! you need login again')
        
        Author = User.objects.filter(username = payload['username'])
        
        if Author is None:
            return JsonResponse({'message': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        deck = Decks.objects.filter(username = payload['username'])
        serializer = DeckSerializer(deck, many=True)
        
        return Response(serializer.data)

class DeckRegisterView(APIView):
    @csrf_exempt
    def post(self, request):
        # Authenticate
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated! you need login first')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated! you need login again')
        
        # Authorization
        
        Author = User.objects.filter(username = payload['username'])
        
        if Author is None:
            return JsonResponse({'message': 'User or Deck Not Found'}, status=status.HTTP_404_NOT_FOUND)
            
        
        data = {
            'username': payload['username'],
            'name_deck': request.data['name_deck'],
            'card': []
        }
        serializer = DeckSerializer(data = data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({'message': 'Successful Registration Deck!!!', 'deck': serializer.data}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PickDeck(APIView):
    @csrf_exempt
    def get(self, request, nd):
        token = request.headers.get('jwt')
        
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        deck = Decks.objects.filter(name_deck=nd, username=payload['username'])
        if deck is None:
            return JsonResponse({'message': 'Deck not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DeckSerializer(deck , many=True)
        return Response(serializer.data)
    
class SaveDeck(APIView):
    @csrf_exempt
    def put(self, request, pk):
        token = request.headers.get('jwt')
        
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        print(request.data['name_deck'])
        Author = Decks.objects.filter(username = payload['username'], name_deck= request.data['name_deck'])
        
        if Author is None:
            return JsonResponse({'message': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        deck = Decks.objects.get(pk=pk)
        
        
        if deck is None:
            return JsonResponse({'message': 'Deck not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeckSerializer(deck,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        