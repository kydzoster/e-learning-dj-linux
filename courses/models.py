from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    # who created this course
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    # The subject this course belongs to
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    # The title of the course
    title = models.CharField(max_length=200)
    # for the URL
    slug = models.SlugField(max_length=200, unique=True)
    # TextField column to store an overview of the course
    overview = models.TextField()
    # date and time when the course was created, it is set automatically
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

# each course is divided into several modules
class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
