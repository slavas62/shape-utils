from django.contrib.gis.geos import GEOSGeometry
from django.db import models
import json
import datetime
import decimal

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, GEOSGeometry):
            return json.JSONDecoder().decode(obj.geojson)
        if isinstance(obj, models.Model):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

def geojsondata(features, geometry_field='geometry'):
    data = {
        'type': 'FeatureCollection',
        'features': [],
    }
    for entry in features:
        feature = {
            'type': 'Feature',
            'geometry': entry.get(geometry_field, None),
            'properties': {},
        }
        for k, v in entry.iteritems():
            if k != geometry_field:
                feature['properties'][k] = v
        data['features'].append(feature)
    return data

def geojson(*args, **kwargs):
    encoder = JSONEncoder()
    data = geojsondata(*args, **kwargs)
    return encoder.encode(data)
