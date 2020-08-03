from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField


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
    # ordering is calculated with respect to the course
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    # limit_choices argument will limit the ContentType objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={
        # model_in field lookup will filter the query to the ContentType objects
        'model__in':('text','video','image','file')
    })
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    # order is calculated with respect to the module field
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

# AThis will define fields which will get included in all child models.
# there wont be a database table for ItemBase() class, due to being an abstract model
class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

# stores content
class Text(ItemBase):
    content = models.TextField()

# stores files, e.g. PDF
class File(ItemBase):
    file = models.FileField(upload_to='files')

# stores images
class Image(ItemBase):
       file = models.FileField(upload_to='images')

# stores videos. through url
class Video(ItemBase):
    url = models.URLField()