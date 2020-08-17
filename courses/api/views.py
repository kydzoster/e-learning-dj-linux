from rest_framework import generics
from ..models import Subject
from .serializers import SubjectSerializer


class SubjectListView(generics.ListAPIView):
    # retrieves objects
    queryset = Subject.objects.all()
    # serializes objects
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    # retrieves objects
    queryset = Subject.objects.all()
    # serializes objects
    serializer_class = SubjectSerializer