from rest_framework import serializers
from .models import User, Decks

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only':True}
        }
        
    def create(self, validate_data):
        password = validate_data.pop('password', None)
        instance = self.Meta.model(**validate_data)
        if password is not None:
            instance.set_password(password)
        instance.save()    
        return instance
    
class DeckSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        db_table = 'decks'
        model = Decks
        fields = ('username', 'name_deck', 'card')