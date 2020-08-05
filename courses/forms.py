from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

# This function allows to build a model 
# formset dynamically for the Module objects related to a Course object
ModuleFormSet = inlineformset_factory(
    Course, Module,
    # Will be included in each form of tthe formset
    fields=['title', 'description'],
    # Allows to set the number of empty extra forms to display in the formset
    extra=2,
    # Boolean field in the form of checkbox input. Marks the objects for delete
    can_delete=True
)