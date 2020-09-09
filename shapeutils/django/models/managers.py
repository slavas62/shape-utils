from django.contrib.gis.db import models
from shapeutils.django.serializers import geojson
from shapeutils.convert import geojson_to_zipshape
from shapeutils.django.models.mappers import ModelMapper

class ZippedShapeQuerySet(models.query.GeoQuerySet):
    
    def zipped_shape(self, mapper=ModelMapper(), fields=None, **kwargs):
        geo_field = self.query._geo_field()
        objects = []
        for o in self.select_related():
            d = mapper.get_dict(o, fields)
            d.update({geo_field.name: getattr(o, geo_field.name, None)})
            objects.append(d)
        return geojson_to_zipshape(geojson(objects, geo_field.name), **kwargs)

class ZippedShapeManager(models.GeoManager):
    
    def get_query_set(self):
        return ZippedShapeQuerySet(self.model, using=self._db)
    
    def zipped_shape(self, *args, **kwargs):
        return self.get_query_set().zipped_shape(*args, **kwargs)
