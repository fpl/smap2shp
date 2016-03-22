#!/usr/bin/env python
#
# This little script converts SMAP HDF5 files in ESRI shapefile
# by exctracting only soil moisture values. 
# 

import sys
import os
import glob
import h5py
import numpy as np
import fiona
from fiona.crs import from_epsg

prog = __file__
if len(sys.argv) < 2:
    print 'usage %s file ...' % __file__
    sys.exit(0)

files = glob.glob(sys.argv[1])
for f in files:
    print f
    with h5py.File(f) as h5f:
        root = h5f.get('Soil_Moisture_Retrieval_Data')
        lats = h5f.get('Soil_Moisture_Retrieval_Data/latitude')
        np_lats = np.array(lats)
        longs = h5f.get('Soil_Moisture_Retrieval_Data/longitude')
        np_longs = np.array(longs)
        sm = h5f.get('Soil_Moisture_Retrieval_Data/soil_moisture')
        np_sm = np.array(sm)
        (base,ext) = os.path.splitext(os.path.basename(f))
        outshp = base + '.shp'
        with fiona.open(outshp,
                'w',
                crs=from_epsg(4326),
                driver='ESRI Shapefile',
                schema={'geometry' : 'Point',
                        'properties' : {'soil_moist' : 'float'}}
                ) as dst:
            for lat, lon, s in np.nditer([np_lats,np_longs,np_sm]):
                if s != -9999:
                    geom = {'type' : 'Point', 'coordinates' : [lon, lat]}
                    feature = {'type': 'Feature', 'geometry' : geom, 'properties'
                            : {'soil_moist' : float(s)}}
                    dst.write(feature)
