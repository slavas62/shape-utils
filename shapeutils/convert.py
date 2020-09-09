import os
import re
from osgeo import ogr
from .utils import InMemoryZip
from .utils import tempdir

ogr.DontUseExceptions()
ogr.UseExceptions()

GEOMETRY_TYPES = ['POINT', 'MULTIPOINT', 'LINESTRING', 'MULTILINESTRING', 'POLYGON', 'MULTIPOLYGON', 'GEOMETRYCOLLECTION']

class ConvertError(Exception):
    pass

def ogr_layer_to_zip(ogr_layer, vector_name='geometry', driver_name='ESRI Shapefile'):
    driver = ogr.GetDriverByName(driver_name)
    if not driver:
        raise ConvertError('Unknown driver')
    
    with tempdir() as vector_dir:
        ds = driver.CreateDataSource(vector_dir, ['ENCODING=UTF-8'])
        splited_shape = False
        try:
            ds.CopyLayer(ogr_layer, vector_name, ['ENCODING=UTF-8'])
        except RuntimeError as e:
            if driver_name == 'ESRI Shapefile':
                for geom_type in GEOMETRY_TYPES:
                    ogr_layer.SetAttributeFilter('OGR_GEOMETRY="%s"' % geom_type)
                    if not ogr_layer.GetFeatureCount():
                        continue
                    vector_type_name = '%s_%s' % (vector_name, geom_type.lower())
                    try:
                        ds.CopyLayer(ogr_layer, vector_type_name, ['ENCODING=UTF-8'])
                    except RuntimeError as e:
                        raise ConvertError(*e.args)
                splited_shape = True
            else:
                raise ConvertError(*e.args)
        finally:
            ds.Release()
        files = os.listdir(vector_dir)
        
        # Exclude files from first CopyLayer try
        if splited_shape:
            files = [f for f in files if not re.match('%s\.\w{3}' % vector_name, f)]
            
        z = InMemoryZip()
        for filename in files:
            fullpath = os.path.join(vector_dir, filename)
            if os.path.isfile(fullpath):
                z.write(fullpath, filename.decode('utf-8'))
        z.close()
        data = z.read()
    return data

def ogr_layer_to_zipshape(ogr_layer, shape_name='shape'):
    return ogr_layer_to_zip(ogr_layer, shape_name)

def geojson_to_zip(geojson, *args, **kwargs):
    if isinstance(geojson, unicode):
        geojson = geojson.encode('utf-8')
    ds = ogr.Open(geojson)
    if not ds:
        raise ConvertError('Could not read geojson')
    return ogr_layer_to_zip(ds.GetLayer(0), *args, **kwargs)

def geojson_to_zipshape(geojson, shape_name='shape', **kwargs):
    return geojson_to_zip(geojson, shape_name)
