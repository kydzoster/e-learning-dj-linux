from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)
    # check if the value exists for this field in the model instance
    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            # if there is no current value
            try:
                # builds a querySet to retrieve all objects for the fields model
                qs = self.model.objects.all()
                if self.for_fields:
                    # if there are any field names in the for_fields attribute of the field,
                    # calculates the order with respect to the given fields
                    query = {field: getattr(model_instance, field)\
                    for field in self.for_fields}
                    qs = qs.filter(**query)
                # retrieve the object with the highest order, order of the last item
                last_item = qs.latest(self.attname)
                # when object is found, add 1 to the highest order found
                value = last_item.order + 1
            # object is not found, assumes it is the first one and assign the order 0 to it
            except ObjectDoesNotExist:
                value = 0
            # assign the calculated order to the fields value in the model instance and return it
            setattr(model_instance, self.attname, value)
            return value
        else:
            # if the model instance has a value for the current field, use it instead of calculating it
            return super().pre_save(model_instance, add)
