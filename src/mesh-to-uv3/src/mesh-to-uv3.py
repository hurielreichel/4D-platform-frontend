#!/usr/bin/python
#  mesh-to-uv3
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

import pymesh
from struct import pack
import argparse
import math

t_argparse = argparse.ArgumentParser()
t_argparse.add_argument( '-i', '--mesh', type=str  , help='mesh path' )
t_argparse.add_argument( '-o', '--uv3', type=str  , help='uv3 file path' )
t_argparse.add_argument( '-s', '--swiss', type=int, default=0, help='whether coordinates are in the swiss system CH1903+ (1), or not (0). Default to zero')
t_argparse.add_argument( '--scaling', type=int, default=0, help='whether SITG Scaling should be applied (1) or not(0). Default to zero')
t_args = t_argparse.parse_args()

# Borrowed and Adapted from Aaron Schmocker [aaron@duckpond.ch]
# Source: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/topics/survey/sys/refsys/projections.html (see PDFs under "Documentation")
# github script: https://github.com/hurielreichel/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py
class GPSConverter(object):
    '''
    GPS Converter class which is able to perform convertions between the 
    CH1903 and WGS84 system.
    '''
    # Convert CH y/x/h to WGS height
    def CHtoWGSheight(self, y, x, h):
        # Axiliary values (% Bern)
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
        h = (h + 49.55) - (12.60 * y_aux) - (22.64 * x_aux)
        return h

    # Convert CH y/x to WGS lat
    def CHtoWGSlat(self, y, x):
        # Axiliary values (% Bern)
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
        lat = (16.9023892 + (3.238272 * x_aux)) + \
                - (0.270978 * pow(y_aux, 2)) + \
                - (0.002528 * pow(x_aux, 2)) + \
                - (0.0447 * pow(y_aux, 2) * x_aux) + \
                - (0.0140 * pow(x_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lat = (lat * 100) / 36
        return lat

    # Convert CH y/x to WGS long
    def CHtoWGSlng(self, y, x):
        # Axiliary values (% Bern)
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
        lng = (2.6779094 + (4.728982 * y_aux) + \
                + (0.791484 * y_aux * x_aux) + \
                + (0.1306 * y_aux * pow(x_aux, 2))) + \
                - (0.0436 * pow(y_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lng = (lng * 100) / 36
        return lng

    def LV03toWGS84(self, east, north, height):
        '''
        Convert LV03 to WGS84 Return a array of double that contain lat, long,
        and height
        '''
        d = []
        d.append(self.CHtoWGSlat(east, north))
        d.append(self.CHtoWGSlng(east, north))
        d.append(self.CHtoWGSheight(east, north, height))
        return d
    
pm_output = t_args.uv3
mesh = pymesh.load_mesh(t_args.mesh)

with open( pm_output, mode='wb' ) as uv3:

    #looping for the triangles
    for i in range(mesh.num_faces):
        
        idx_1=mesh.faces[i][0]
        idx_2=mesh.faces[i][1]
        idx_3=mesh.faces[i][2]
        
        #getting coordinates of every vertex in the triangle (3)
        vertex_1 = mesh.vertices[idx_1]
        vertex_2 = mesh.vertices[idx_2]
        vertex_3 = mesh.vertices[idx_3]
   
        if (t_args.scaling != 0):
       
            #scaling of the coordinates - This is most probably changing from file to file. The usage below referes to SITG's datasets
            conv_vertex_1 = [(vertex_1[0] - 2480000) * -1, (vertex_1[1] - 1109000) * -1, vertex_1[2]]
            conv_vertex_2 = [(vertex_2[0] - 2480000) * -1, (vertex_2[1] - 1109000) * -1, vertex_2[2]]
            conv_vertex_3 = [(vertex_3[0] - 2480000) * -1, (vertex_3[1] - 1109000) * -1, vertex_3[2]]
            
        else:
            
            conv_vertex_1 = [vertex_1[0], vertex_1[1], vertex_1[2]]
            conv_vertex_2 = [vertex_2[0], vertex_2[1], vertex_2[2]]
            conv_vertex_3 = [vertex_3[0], vertex_3[1], vertex_3[2]]
            
        if (t_args.swiss != 0):
            
            #conversion to WGS84 from the swiss coordinate system CH1903+
            converter = GPSConverter()
            wgs84_1 = converter.LV03toWGS84(conv_vertex_1[0], conv_vertex_1[1], conv_vertex_1[2])
            wgs84_2 = converter.LV03toWGS84(conv_vertex_2[0], conv_vertex_2[1], conv_vertex_2[2])
            wgs84_3 = converter.LV03toWGS84(conv_vertex_3[0], conv_vertex_3[1], conv_vertex_3[2])
            
            vertex1 = [wgs84_1[1] * (math.pi/180), wgs84_1[0] * (math.pi/180), wgs84_1[2]]
            vertex2 = [wgs84_2[1] * (math.pi/180), wgs84_2[0] * (math.pi/180), wgs84_2[2]]
            vertex3 = [wgs84_3[1] * (math.pi/180), wgs84_3[0] * (math.pi/180), wgs84_3[2]]
        
            #conversion to radians
            vertex1 = [wgs84_1[1] * (math.pi/180), wgs84_1[0] * (math.pi/180), wgs84_1[2]]
            vertex2 = [wgs84_2[1] * (math.pi/180), wgs84_2[0] * (math.pi/180), wgs84_2[2]]
            vertex3 = [wgs84_3[1] * (math.pi/180), wgs84_3[0] * (math.pi/180), wgs84_3[2]]
        
        else:
            
            #conversion to radians
            vertex1 = [conv_vertex_1[1] * (math.pi/180), conv_vertex_1[0] * (math.pi/180), conv_vertex_1[2]]
            vertex2 = [conv_vertex_2[1] * (math.pi/180), conv_vertex_2[0] * (math.pi/180), conv_vertex_2[2]]
            vertex3 = [conv_vertex_3[1] * (math.pi/180), conv_vertex_3[0] * (math.pi/180), conv_vertex_3[2]]
            
        #writing the uv3 file
        record = pack('<dddBBBB', vertex1[0], vertex1[1], vertex1[2], 3, 173, 73, 74 )
        uv3.write( record )
        record = pack('<dddBBBB', vertex2[0], vertex2[1], vertex2[2], 3, 173, 73, 74 )
        uv3.write( record )
        record = pack('<dddBBBB', vertex3[0], vertex3[1], vertex3[2], 3, 173, 73, 74 )
        uv3.write( record )
        

