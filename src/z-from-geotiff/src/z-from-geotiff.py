#!/usr/bin/python
#  z-from-geotiff
#
#     Huriel Reichel - huriel.ruan@gmail.com     
#     Nils Hamel - nils.hamel@bluewin.ch
#     
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
from struct import pack

import argparse
import math
import sys
import os
import numpy as np
import time
from matplotlib import cm

def pm_assign_z( pm_input, pm_output, pm_raster_z, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_w, pm_h, palette, height): 
    
   # Defining minimum and maximum values for the three dimensional variable
    min_z = pm_band_z.GetStatistics(True, True)[0]
    max_z = pm_band_z.GetStatistics(True, True)[1]
        
    # defining colour palette
    pal = cm.get_cmap(palette, 100) 
    
    if ( height == 1 ):
    
        print( "computing heights and colours")
        
        # create output stream #
        with open( pm_output, mode='wb' ) as uv3:

           # compute raster position #
           for x in range(pm_width):
               for y in range(pm_height):
                   pm_z = pm_raster_z[y][x]
                   feat_scal = (pm_z - min_z) / (max_z - min_z)
                   col = pal(feat_scal)
                   pm_r = int( col[0] * 255 )
                   pm_g = int( col[1] * 255 )
                   pm_b = int( col[2] * 255 )
                   
                   # setting no data as black / same colour as eratosthene's background
                   if (pm_z <= -4e38):
                       
                       pm_r = 7
                       pm_g = 10
                       pm_b = 12
                   
                   pm_rx = ( ( x * pm_pw ) + pm_x ) * ( math.pi/180 )
                   pm_ry = ( pm_y - ( y * pm_ph ) ) * ( math.pi/180 )
                   pm_buffer = pack( '<dddBBBB', pm_rx, pm_ry, pm_z, 1, pm_r, pm_g, pm_b )
                   uv3.write( pm_buffer )
                   #print( pm_rx, pm_ry, 0, 1, pm_r, pm_g, pm_b ) # in chase you want to print results as the former Octave code
       
    else:
        
        print( "not computing heights, only colours")
         
        # create output stream #
        with open( pm_output, mode='wb' ) as uv3:

           # compute raster position #
           for x in range(pm_width):
               for y in range(pm_height):
                   pm_z = pm_raster_z[y][x]
                   feat_scal = (pm_z - min_z) / (max_z - min_z)
                   col = pal(feat_scal)
                   pm_r = int( col[0] * 255 )
                   pm_g = int( col[1] * 255 )
                   pm_b = int( col[2] * 255 )
                       
                   # setting no data as black / same colour as eratosthene's background
                   if (pm_z <= -4e38):
                       
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
pm_argparse.add_argument( '-p', '--palette', default='inferno', type=str , help='matplotlib colour palette name')
pm_argparse.add_argument( '-height', '--height', default=1, type=int, help='whether height should be assigned (1) or not (0)')

# read argument and parameters #
pm_args = pm_argparse.parse_args()

# GDAL configuration #
gdal.UseExceptions()

# GDAL open geotiff file #
pm_geotiff = gdal.Open( pm_args.input )
#pm_geotiff = gdal.Open( pm_input ) #in chase of working inside a GUI

# retrieve raster data #
pm_band_z = pm_geotiff.GetRasterBand(1)

# retrieve raster no data value #
pm_band_z.SetNoDataValue(-4e38)
pm_nodata = pm_band_z.GetNoDataValue()

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
pm_raster_z = pm_band_z.ReadAsArray( 0, 0, pm_width, pm_height )

# check no data value #
if pm_nodata is not None:   

    # replace no data value #
    pm_raster_z = np.where( pm_raster_z < -3e38, int( -4e38 ), pm_raster_z )

# display message #
print( 'Processing file : ' + os.path.basename( pm_args.input ) + '...' )

tic = time.time()

# process file #
pm_assign_z( pm_args.input, pm_args.output, pm_raster_z, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_width, pm_height, pm_args.palette, pm_args.height )

toc = time.time()

# exit script #
sys.exit(f'Done. Elapsed time = {(toc-tic):.2f} seconds.' )
