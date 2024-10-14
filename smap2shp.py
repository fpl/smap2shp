#!/usr/bin/env python3
#
#   This little script converts SMAP L3 HDF5 files in ESRI shapefile
#   by exctracting only soil moisture values.
#
#   Copyright (C) 2016-2024 Francesco P. Lovergine <francesco.lovergine@cnr.it>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import glob
import h5py
import numpy as np
import fiona
from fiona.crs import from_epsg

prog = __file__
if len(sys.argv) < 3 or sys.argv[1] not in ['am', 'pm']:
    print('usage %s [am|pm] file ...' % __file__)
    sys.exit(0)

period = sys.argv[1]

suffix = period.upper()
varsuffix = ''
if period == 'pm':
    varsuffix = '_' + period

files = glob.glob(sys.argv[2])
for f in files:
    print(f)
    with h5py.File(f) as h5f:
        root = h5f.get('Soil_Moisture_Retrieval_Data_'+suffix)
        lats = h5f.get('Soil_Moisture_Retrieval_Data_%s/latitude%s' % (suffix, varsuffix))
        np_lats = np.array(lats)
        longs = h5f.get('Soil_Moisture_Retrieval_Data_%s/longitude%s' % (suffix, varsuffix))
        np_longs = np.array(longs)
        sm = h5f.get('Soil_Moisture_Retrieval_Data_%s/soil_moisture%s' % (suffix, varsuffix))
        np_sm = np.array(sm)
        sm_dca = h5f.get('Soil_Moisture_Retrieval_Data_%s/soil_moisture_dca%s' % (suffix, varsuffix))
        np_sm_dca = np.array(sm_dca)
        sm_err = h5f.get('Soil_Moisture_Retrieval_Data_%s/soil_moisture_error%s' % (suffix, varsuffix))
        np_sm_err = np.array(sm_err)
        flag = h5f.get('Soil_Moisture_Retrieval_Data_%s/retrieval_qual_flag_dca%s' % (suffix, varsuffix))
        np_flag = np.array(flag)

        (base,ext) = os.path.splitext(os.path.basename(f))
        outshp = base + '.shp'
        with fiona.open(outshp,
                'w',
                crs=from_epsg(4326),
                driver='ESRI Shapefile',
                schema={'geometry' : 'Point',
                        'properties' : {'soil_moist' : 'float', 'sm_dca' : 'float', 'sm_err' : 'float'}}
                ) as dst:
            for lat, lon, s, d, e, f in np.nditer([np_lats,np_longs,np_sm,np_sm_dca,np_sm_err,np_flag]):
                if s != -9999 and ~(f & 1):
                    geom = {'type' : 'Point', 'coordinates' : [lon, lat]}
                    feature = {'type': 'Feature', 'geometry' : geom, 'properties'
                               : {'soil_moist' : float(s), 'sm_dca': float(d), 'sm_err': float(e)}}
                    dst.write(feature)
