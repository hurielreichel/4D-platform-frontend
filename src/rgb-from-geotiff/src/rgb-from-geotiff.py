#!/usr/bin/env python3
#  rgb-from-geotiff
#
#     Huriel Reichel - huriel.ruan@gmail.com
#     Nils Hamel - nils.hamel@bluewin.ch
#     Copyright (c) 2020 Republic and Canton of Geneva
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from osgeo import gdal
import osr
from struct import pack

import argparse
import math
import sys
import os
import numpy as np

# Borrowed and Adapted from Aaron Schmocker [aaron@duckpond.ch]
# Source: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/topics/survey/sys/refsys/projections.html (see PDFs under "Documentation")
# guthub script: https://github.com/hurielreichel/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py

def pm_assign_rgb( pm_input, pm_output, pm_raster_r, pm_raster_g, pm_raster_b, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_w, pm_h): 
    
        # create output stream #
        with open( pm_output, mode='wb' ) as uv3:

           # compute raster position #
           for x in range(pm_width):
               for y in range(pm_height):
                   pm_r = pm_raster_r[y][x]
                   pm_g = pm_raster_g[y][x]
                   pm_b = pm_raster_b[y][x]
                   
                   if (pm_r < 0 or pm_g < 0 or pm_b < 0):
                       
                       pm_r = 7
                       pm_g = 10
                       pm_b = 12

                   pm_rx = ( ( x * pm_pw ) + pm_x ) * ( math.pi/180 )
                   pm_ry = ( pm_y - ( y * pm_ph ) ) * ( math.pi/180 )
                   pm_buffer = pack( '<dddBBBB', pm_rx, pm_ry, 0, 1, pm_r, pm_g, pm_b )
                   uv3.write( pm_buffer )
                   #print( pm_rx, pm_ry, 0, 1, pm_r, pm_g, pm_b ) # in chase you want to print results as the former Octave code
                
#
#   source - main function
#

# create argument parser #
pm_argparse = argparse.ArgumentParser()

# argument and parameter directive #
pm_argparse.add_argument( '-i', '--input', type=str  , help='geotiff path'    )
pm_argparse.add_argument( '-o', '--output' , type=str  , help='uv3 output path' )
pm_argparse.add_argument( '-r', '--red' , type=int, default=1, help='integer refering to the number of the band to replace (or not) the red band, default being 1' )
pm_argparse.add_argument( '-g', '--green' , type=int, default=2, help='integer refering to the number of the band to replace (or not) the green band, default being 2' )
pm_argparse.add_argument( '-b', '--blue' , type=int, default=3, help='integer refering to the number of the band to replace (or not) the blue band, default being 3' )
pm_argparse.add_argument( '-s', '--swiss', type=int, default=0 , help='if set as true (1), this is converting data from the swiss coordinate system CH1093+ (EPSG:2056) to WGS84')

# read argument and parameters #
pm_args = pm_argparse.parse_args()

# GDAL configuration #
gdal.UseExceptions()

# GDAL open geotiff file #
pm_geotiff = gdal.Open( pm_args.input )

# get the existing coordinate system
old_cs = osr.SpatialReference()
old_cs.ImportFromWkt(pm_geotiff.GetProjectionRef())

# create the new coordinate system
wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""

new_cs = osr.SpatialReference()
new_cs.ImportFromWkt(wgs84_wkt)

if (old_cs != new_cs):
    pm_geotiff = gdal.Warp('', pm_geotiff, dstSRS='EPSG:4326', format='VRT', outputType=gdal.GDT_Int16)

# retrieve raster data #
pm_band_r = pm_geotiff.GetRasterBand(pm_args.red)
pm_band_g = pm_geotiff.GetRasterBand(pm_args.green)
pm_band_b = pm_geotiff.GetRasterBand(pm_args.blue)

# retrieve raster no data value #
pm_nodata = pm_band_r.GetNoDataValue()

# extract raster resolution #
pm_width = pm_geotiff.RasterXSize
pm_height = pm_geotiff.RasterYSize

# retrieve raster transformation #
pm_gtrans = pm_geotiff.GetGeoTransform()

# retrieve raster geographic parameters #
pm_x = pm_gtrans[0] # origin x #
pm_y = pm_gtrans[3] # origin y #
pm_pw = pm_gtrans[1] # pixel width #
pm_ph = -pm_gtrans[5] # pixel height #
    
# format raster pm_raster
pm_raster_r = pm_band_r.ReadAsArray( 0, 0, pm_width, pm_height )
pm_raster_g = pm_band_g.ReadAsArray( 0, 0, pm_width, pm_height )
pm_raster_b = pm_band_b.ReadAsArray( 0, 0, pm_width, pm_height ) 
pm_raster = np.array([[pm_raster_r], [pm_raster_g], [pm_raster_b]])

# check no data value #
if pm_nodata is not None:   

    # replace no data value #
    pm_raster = np.where( pm_raster == int (pm_nodata), int( 0 ), pm_raster)

# display message #
print( 'Processing file : ' + os.path.basename( pm_args.input ) + '...' )

# process file #
pm_assign_rgb( pm_args.input, pm_args.output, pm_raster_r, pm_raster_g, pm_raster_b, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_width, pm_height )

# exit script #
sys.exit( 'Done' )
