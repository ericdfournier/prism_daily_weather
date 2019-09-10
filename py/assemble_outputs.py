#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 08:01:14 2019

@author: edf
"""

#%% Package Imports

import pandas as pd
import geopandas as gpd
import shapely as sh
import numpy as np
import os

#%% Read Data

os.chdir('/Users/edf/repos/prism_daily_weather/scratch')

#%% Read Raw Data

tmin = pd.read_csv('PRISM_tmin_stable_4kmM2_daily_final.csv')
tmax = pd.read_csv('PRISM_tmax_stable_4kmM2_daily_final.csv')
tmean = pd.read_csv('PRISM_tmean_stable_4kmM2_daily_final.csv')
print('Data Loaded...')

#%% Extract Base Parameters

coords = tmin.loc[:,['x','y']]
coords['x'] = np.around(coords['x'], decimals = 12)
coords['y'] = np.around(coords['y'], decimals = 12)
datetime = pd.to_datetime(tmin['dt'], format='%Y%m%d')

#%% Assemble GEOID

lat_lng_tuples = list(coords.itertuples(index=False, name=None))
unique_lat_lng = list(dict.fromkeys(lat_lng_tuples))

i = 0
geohash = {}
for u in unique_lat_lng:
    geohash[u] = i
    i = i+1
    
geoid = []
for i, row in coords.iterrows():
    geoid.append(geohash[tuple(row[['x','y']].values)])
    
print('Points Hashed...')
    
#%% Generate Attribute Data Structure

df = tmin.loc[:,['tmin']]
df['geoid'] = geoid
df['dt'] = datetime
df['tmax'] = tmax['tmax']
df['tmean'] = tmean['tmean']
df['year'] = datetime.dt.year
df['month'] = datetime.dt.month
df['day'] = datetime.dt.day

# Re-Order Columns
df = df[['geoid', 'dt', 'year', 'month', 'day', 'tmax', 'tmean', 'tmin']]

#%% Generate Point Shapefile

points = [sh.geometry.Point(l[0], l[1]) for l in unique_lat_lng] 
geolocated_data = pd.DataFrame(points, columns=['geometry'], index=list(geohash.values()))

crs = {'init': 'epsg:4269'}
gdf_4269 = gpd.GeoDataFrame(geolocated_data, crs = crs, geometry = 'geometry', index = geolocated_data.index)
gdf_3310 = gdf_4269.to_crs({'init': 'epsg:3310'})
print('Outputs Assembled...')

#%% Output to Files

gdf_4269.to_file('/Users/edf/repos/prism_daily_weather/final/point_grid_4269.shp')
gdf_3310.to_file('/Users/edf/repos/prism_daily_weather/final/point_grid_3310.shp')
df.to_csv('/Users/edf/repos/prism_daily_weather/final/temperature_data.csv', index=False)
print('Outputs Written to File...')
