from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    # override get_queryset() method of the view to retrieve only courses created by the current user
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

# retrieves objects that belong to current user
class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

# retrieves objects that belong to current user, when validate can alter only his own objects
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    # the model used for querysets, used by all views
    model = Course
    # fields of the model to build the model form of the CreateView and UpdateView
    fields = ['subject', 'title', 'slug', 'overview']
    # used after the form is successfully submited , altered or deleted
    success_url = reverse_lazy('manage_course_list')

# template view for creation, editing and deleting
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

# Lists the courses created by the user
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
# Create a new course object
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    pass

# allows to edit an existing course object
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    pass

# defines a specific atribute for a template to confirm the course deletion
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
