from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    # the course on which the user will be enrolled, this field wont be seen by the user
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput)
