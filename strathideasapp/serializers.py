from rest_framework import serializers
from .models import Ideas


class IdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ideas
        fields = (
            'title', 'user', 'problem_statement'
        )
