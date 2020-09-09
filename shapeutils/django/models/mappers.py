from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.models import model_to_dict

class ModelMapper(object):
    
    def get_dict(self, obj, fields=None):
        if fields:
            fields = [f for f in obj._meta.fields[:] if f.name in fields]
        else:
            fields = obj._meta.fields[:]
        related_fields = [f for f in fields if isinstance(f, ForeignKey)]
        for f in fields:
            if isinstance(f, ManyToManyField):
                fields.remove(f)
        obj_dict = model_to_dict(obj, [f.name for f in fields], [f.name for f in related_fields])
        for f in related_fields:
            obj_dict[f.name] = getattr(obj, f.name, None)
        for k, v in obj_dict.iteritems():
            if hasattr(self, 'process_%s' % k):
                obj_dict[k] = getattr(self, 'process_%s' % k)(k, v, obj)
        return obj_dict
    