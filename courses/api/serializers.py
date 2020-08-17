from rest_framework import serializers
from ..models import Subject
from ..models import Course, Module


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']

# This will provide serialization for the Module model.
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    # this will serve as a Moduleserializer for CourseSerializer which will 
    # serialize multiple objects and it will be only read-only 
    # and wont be included in any input to create or update objects
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'modules']
