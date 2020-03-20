from rest_framework import serializers
from api.models import *


class TeamSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    