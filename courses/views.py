from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Count
from django.core.cache import cache
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from .models import Course, Module, Content, Subject
from .forms import ModuleFormSet
from students.forms import CourseEnrollForm


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

# this will allow to create and updatedifferent mmodels contents
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    # check that given model name is one of the four content models(text, video, image, file)
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            # obtains the actual class for the given model name
            return apps.get_model(app_label='courses', model_name=model_name)
        # if not valid return None
        return None

    def get_form(self, model, *args, **kwargs):
        # dynamic form which excludes specific parameters
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)
    # receives URL parameters and stores the coressponding module, model and content object as class attributes
    def dispatch(self, request, module_id, model_name, id=None):
        # module_id, ID for the module that content is/will be associated with
        # id, the ID of the object that is being updated
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        # model_name, name of the content to create/update
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    # builds model form for text, video, image, file, that is being updated
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})
    # Builds a model form, passing any submited data and files to it.
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        # validates it
        if form.is_valid():
            # when valid create new object and 
            obj = form.save(commit=False)
            # assign user as its owner
            obj.owner = request.user
            obj.save()
            # check id, if no id provided then
            if not id:
                # create a new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})

# retrieves content object with given ID. deletes the related object.
class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

# This gets Module object with the given ID that belongs to the current user and renders a template with the given module
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        # try to get all students
        subjects = cache.get('all_subjects')
        # if no students found ..
        if not subjects:
            # then retrieve all available courses for each subject and number of courses
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        # retrieve all available courses for each subject, 
        # including the total number of modules contained in each course
        courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            # retrieve corresponding subject object and limit 
            # the query to the courses that belong to the given subject
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        # render the objects to a template and return an HTTP response
        return self.render_to_response({
            'subjects': subjects,
            'subject': subject,
            'courses': courses
        })


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    # this method will include the enrollement form in the context for rendering templates
    # it will initialize the hidden course field of the form with the current course object 
    # so it can be submitted directly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context