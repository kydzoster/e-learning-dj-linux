from rest_framework import generics
from ..models import Subject, Course
from .serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from .permissions import IsEnrolled


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
"""
# this will handle student enrolement on course.
class CourseEnrollView(APIView):
    # users will be identified by the credentials set in the Authorization header of the HTTP request
    authentication_classes = (BasicAuthentication,)
    # this will prevent anonymous users from accessing the view
    permission_classes = (IsAuthenticated,)

    # This method will allow only POST method, no other HTTP method is allowed
    def post(self, request, pk, format=None):
        # this retrieves course by pk parameter and raises a 404 if its not found
        course = get_object_or_404(Course, pk=pk)
        # add current user to the students many-to-many relationship of the course
        course.students.add(request.user)
        # return successful response
        return Response({'enrolled': True})"""


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # action decorator with parameter detail=True to specify 
    # that this is an action to be performed on a single object.
    @action(detail=True,
            methods=['post'],
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
    # this will perform action on a single object
    # only GET is allowed, and only users enrolled on course can access its content
    @action(detail=True,
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        # returns the course object
        return self.retrieve(request, *args, **kwargs)