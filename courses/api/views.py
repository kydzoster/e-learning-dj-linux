from rest_framework import generics
from ..models import Subject, Course
from .serializers import SubjectSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication


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

# this will handle student enrolement on course.
class CourseEnrollView(APIView):
    # users will be identified by the credentials set in the Authorization header of the HTTP request
    authentication_classes = (BasicAuthentication,)

    # This method will allow only POST method, no other HTTP method is allowed
    def post(self, request, pk, format=None):
        # this retrieves course by pk parameter and raises a 404 if its not found
        course = get_object_or_404(Course, pk=pk)
        # add current user to the students many-to-many relationship of the course
        course.students.add(request.user)
        # return successful response
        return Response({'enrolled': True})
