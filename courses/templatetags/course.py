from django import template


register = template.Library()

@register.filter
# apply it in templates as object|model_name to get the model name for an object
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None
