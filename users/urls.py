from django.urls import re_path
from .views import RegisterView, LoginView, UserView, LogoutView, DeckRegisterView, DeckView, PickDeck, SaveDeck

urlpatterns = [
    re_path('register', RegisterView.as_view()),
    re_path('login', LoginView.as_view()),
    re_path('user', UserView.as_view()),
    re_path('logout', LogoutView.as_view()),
    re_path('add_deck', DeckRegisterView.as_view()),
    re_path('user_deck', DeckView.as_view()),
    re_path(r'pick_deck/(?P<pk>[0-9]+)$', PickDeck.as_view()),
    re_path(r'save_deck/(?P<pk>[0-9]+)$', SaveDeck.as_view())
]