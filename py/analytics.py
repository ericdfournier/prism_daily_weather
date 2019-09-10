#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:54:32 2019

@author: edf
"""

#%% Package Imports

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

font = {'size': 18}

matplotlib.rc('font', **font)

#%% Read Temp Data

data_root = '/Users/edf/repos/prism_daily_weather/'
os.chdir(data_root)
df = pd.read_csv(data_root + 'final/temperature_data.csv')

#%% Read Spatial Data

gdf = gpd.read_file(data_root + 'final/point_grid_4269.shp')
gdf.columns = ['geoid', 'geometry']

#%% Read Basemap

shape_root = '/Users/edf/repos/prism_daily_weather/ref/'
ladwp = gpd.read_file(shape_root + 'ladwp.shp')
ladwp = ladwp.to_crs({'init': 'epsg:4269'})

#%% Counter Function

def Streak(df, field, thresh, above):
    
    out = df.copy(deep=True)
    new_field = field + '_streak'
    out[new_field] = np.nan
    
    for geoid in out['geoid'].unique():
        sub_df = out.loc[out['geoid'] == geoid]
        if above == True:
            ind = sub_df[field] >= thresh
        else:
            ind = sub_df[field] <= thresh
        counts = np.zeros(len(ind))
        counter = 0
        for n, i in enumerate(ind.values):
            if i == True:
                counter = counter + 1
                counts[n] = counter
            else:
                counter = 0
                counts[n] = counter
        out.loc[ind.index, new_field] = counts
    
    return out

#%% Compute Streak Stats
    
thresh = 35.0
field = 'tmax'
field_name = field + '_streak'
above = True
df = Streak(df, field, thresh, above)
gdfs = {}

for year in df['year'].unique():
    sub = df.loc[df['year'] == year]
    stats = sub.groupby('geoid').agg('max')[field_name]
    roi = stats.loc[stats > 0.0]
    roi_df = roi.to_frame().reset_index(inplace=True)
    out = gdf.merge(roi, on='geoid')
    gdfs[year] = out

#%% Plotting

fig, axs = plt.subplots(3,5, figsize=(20,20))
axs = axs.ravel()
fig.delaxes(axs[-1])

for i, year in enumerate(gdfs.keys()):
    base = ladwp.geometry.boundary.plot(ax=axs[i], color=None, edgecolor='r')
    gdf.plot(figsize=(10,10), markersize=20, ax=base)
    hot = gdfs[year].plot(ax=base, column=field_name, cmap='Spectral_r', markersize=350, categorical=False, legend=True, vmin=0, vmax=21, marker = 's')
    base.set_title(str(year))
    base.set_axis_off()
    xlim = ([ladwp.total_bounds[0],  ladwp.total_bounds[2]])
    ylim = ([ladwp.total_bounds[1],  ladwp.total_bounds[3]])
    base.set_xlim(xlim)
    base.set_ylim(ylim)

fig.tight_layout()

#%% Plotting

fig, axs = plt.subplots(3,5, figsize=(20,20))
axs = axs.ravel()
fig.delaxes(axs[-1])

for i, year in enumerate(gdfs.keys()):
    base = ladwp.geometry.boundary.plot(ax=axs[i], color=None, edgecolor='r')
    gdf.plot(markersize=6, ax=base)
    hot = gdfs[year].plot(ax=base, column=field_name, cmap='Spectral_r', markersize=38, categorical=False, legend=False, vmin=0, vmax=21, marker = 's')
    base.set_title(str(year))
    base.set_axis_off()
    xlim = ([gdf.total_bounds[0],  gdf.total_bounds[2]])
    ylim = ([gdf.total_bounds[1],  gdf.total_bounds[3]])
    base.set_xlim(xlim)
    base.set_ylim(ylim)

fig.tight_layout()