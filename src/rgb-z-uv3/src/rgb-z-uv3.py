#!/usr/bin/python
#  rgb-z-uv3
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

from osgeo  import gdal
from struct import pack

import argparse
import math
import sys
import os
import numpy as np

PM_R2D = ( 180. / math.pi )

#
#   source - interpolation function
#

def pm_raster_interpolate( pm_x, pm_y, pm_raster, pm_nodata ):

    # compute interpolation nodes #
    pm_x1 = int( pm_x )
    pm_y1 = int( pm_y )

    # compute interpolation nodes #
    pm_x2 = pm_x1 + 1
    pm_y2 = pm_y1 + 1

    # interpolation parameter #
    pm_dx = pm_x - pm_x1
    pm_dy = pm_y - pm_y1

    # node values #
    pm_x1y1 = pm_raster[pm_x1][pm_y1] / 1.0
    pm_x1y2 = pm_raster[pm_x1][pm_y2] / 1.0
    pm_x2y1 = pm_raster[pm_x2][pm_y1] / 1.0
    pm_x2y2 = pm_raster[pm_x2][pm_y2] / 1.0

    # interpolation intermediate value #
    pm_dfc = pm_x1y1

    # interpolation intermediate value #
    pm_dfx = pm_x2y1 - pm_x1y1
    pm_dfy = pm_x1y2 - pm_x1y1

    # interpolation intermediate value #
    pm_dfxy = pm_x1y1 + pm_x2y2 - pm_x2y1 - pm_x1y2

    # compute interpolated value #
    return pm_dfx * pm_dx + pm_dfy * pm_dy + pm_dfxy * pm_dx * pm_dy + pm_dfc

def pm_rgb_plus_z(pm_input, pm_raster_z, pm_output, pm_raster_r, pm_raster_g, pm_raster_b, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_w, pm_h):

        # create output stream #
        with open( pm_output, mode='wb' ) as uv3:
            
            for x in range(pm_width):
                for y in range(pm_height):
                    pm_r = pm_raster_r[y][x]
                    pm_g = pm_raster_g[y][x]
                    pm_b = pm_raster_b[y][x]
                   
                    if (pm_r < 0 or pm_g < 0 or pm_b < 0):
                       
                       pm_r = 7
                       pm_g = 10
                       pm_b = 12
                    
                    # compute geographical coordinates from color-tif pixels
                    pm_rx = ( ( x * pm_pw ) + pm_x ) * ( math.pi/180 )
                    pm_ry = ( pm_y - ( y * pm_ph ) ) * ( math.pi/180 )
                    # compute pixel coordinates on the z-value-tif from geographical coordinates
                    pm_zx = ( ( pm_rx * 180/math.pi ) - pm_ztif_x ) / pm_ztif_pw
                    pm_zy = ( pm_ztif_y - ( pm_ry * 180/math.pi ) ) / pm_ztif_ph
               
                    if int( pm_zx ) < 0 or int( pm_zy ) < 0 or int( pm_zx ) + 1 >= pm_w or int( pm_zy ) + 1 >= pm_h:

                        # compute interpolated height #
                        pm_z = 0.0;

                    else:
                        
                        pm_z = pm_raster_interpolate(pm_zy, pm_zx, pm_raster_z, pm_nodata)
                    
                    pm_buffer = pack( '<dddBBBB', pm_rx, pm_ry, pm_z, 1, pm_r, pm_g, pm_b )
                    uv3.write( pm_buffer )
                    #print( pm_rx, pm_ry, pm_z, 1, pm_r, pm_g, pm_b ) # in chase you want to print results as the former Octave code
   
#
#   source - main function
#

# create argument parser #
pm_argparse = argparse.ArgumentParser()

# argument and parameter directive #
pm_argparse.add_argument( '-i', '--input', type=str  , help='input rgb geotiff path'    )
pm_argparse.add_argument( '-d', '--dem', type=str  , help='input digital elevation model geotiff path'    )
pm_argparse.add_argument( '-o', '--output' , type=str  , help='uv3 output path' )
pm_argparse.add_argument( '-r', '--red' , type=int, default=1, help='integer refering to the number of the band to replace (or not) the red band, default being 1' )
pm_argparse.add_argument( '-g', '--green' , type=int, default=2, help='integer refering to the number of the band to replace (or not) the green band, default being 2' )
pm_argparse.add_argument( '-b', '--blue' , type=int, default=3, help='integer refering to the number of the band to replace (or not) the blue band, default being 3' )

# read argument and parameters #
pm_args = pm_argparse.parse_args()

# GDAL configuration #
gdal.UseExceptions()

# GDAL open geotiff file #
pm_geotiff = gdal.Open( pm_args.input )

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

# GDAL open geotiff file #
pm_dem = gdal.Open( pm_args.dem )

# retrieve raster data #
pm_band_z = pm_dem.GetRasterBand(1)
pm_nodata_z = pm_band_z.SetNoDataValue(0)

pm_ztif_x = pm_gtrans[0] # origin x #
pm_ztif_y = pm_gtrans[3] # origin y #
pm_ztif_pw = pm_gtrans[1] # pixel width #
pm_ztif_ph = -pm_gtrans[5] # pixel height #

pm_z_width = pm_dem.RasterXSize
pm_z_height = pm_dem.RasterYSize

# format raster pm_raster_z
pm_raster_z = pm_band_z.ReadAsArray( 0, 0, pm_z_width, pm_z_height )

# check no data value #
if pm_nodata_z is not None:   

    # replace no data value #
    pm_raster_z = np.where( pm_raster_z < -34020000000, int( 0 ), pm_raster_z)
    
# display message #
print( 'Processing files : ' + os.path.basename( pm_args.input ) + ' and ' + os.path.basename( pm_args.dem ) + '...' )

# process file #
pm_rgb_plus_z(pm_args.input, pm_raster_z, pm_args.output, pm_raster_r, pm_raster_g, pm_raster_b, pm_x, pm_y, pm_pw, pm_ph, pm_nodata, pm_width, pm_height)

# exit script #
sys.exit( 'Done' )
