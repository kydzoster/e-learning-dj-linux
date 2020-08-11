from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm

# This will allow student registration on site
class StudentRegistrationView(CreateView):
    # path of the template to render this view
    template_name = 'students/student/registration.html'
    # The form for creating objects
    form_class = UserCreationForm
    # the form where to redirect after successful user registration
    success_url = reverse_lazy('student_course_list')
    # execute this form when valid form data has been posted
    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password1'])
        # log user in after they have successfully signed up
        login(self.request, user)
        return result

# this handles student enrollement on courses, only logged in users can access this view
class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])