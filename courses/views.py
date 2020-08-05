from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from .models import Course
from .forms import ModuleFormSet


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
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
    
# Create a new course object
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

# allows to edit an existing course object
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

# defines a specific atribute for a template to confirm the course deletion
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

# This handles the formset to add, update and delete modules for a specific course
# TemplateResponseMixin renders templates and returns an HTTP response
class CourseModuleUpdateView(TemplateResponseMixin, View):
    # This indicates the template to be rendered
    template_name = 'courses/manage/module/formset.html'
    course = None
    # This method will avoid repeating the code to build formset
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    # This takes an HTTP request and attempts to delegate to a lowercase method that matches HTTP method 
    def dispatch(self, request, pk):
        # This method uses shortcut function to get the Course object for the given ID parameter that belongs to the current user
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)
    # executes get request and builds the template together with the current course
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})
    # 
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        # validates all of its forms
        if formset.is_valid():
            # if valid, save it
            formset.save()
            return redirect('manage_course_list')
        # if not valid, renders the template to display any errors
        return self.render_to_response({'course': self.course, 'formset': formset})
