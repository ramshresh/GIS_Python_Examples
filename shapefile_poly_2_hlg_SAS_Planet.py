import os
import csv
import arcpy
from os import path
from arcpy import da
from arcpy import env

wkid = 4326 # wkid code for wgs84
spatial_reference = arcpy.SpatialReference(wkid)

env.overwriteOutput = True

env.workspace = r'M:\Ram\roads\tiles'

polygon_shp = path.join(env.workspace, 'selected_tiles_5km_Bigu_Dissolved.shp')
vertex_csv_path = r'M:\Ram\roads\tiles\pre_2016_may_31poly_vertex.csv'
vertex_hlg_path = r'M:\Ram\roads\tiles\pre_2016_may_31poly_vertex.hlg'

def getPolygonCoordinates(fc):
    """For each polygon geometry in a shapefile get the sequence number and
    and coordinates of each vertex and tie it to the OID of its corresponding
    polygon"""

    vtx_dict = {}
    s_fields = ['OID@', 'Shape@XY']
    
    pt_array = da.FeatureClassToNumPyArray(polygon_shp, s_fields, 
        explode_to_points=True, spatial_reference = spatial_reference)

    for oid, xy in pt_array:
        xy_tup = tuple(xy)
        if oid not in vtx_dict:
            vtx_dict[oid] = [xy_tup]
        # this clause ensures that the first/last point which is listed
        # twice only appears in the list once
        elif xy_tup not in vtx_dict[oid]:
            vtx_dict[oid].append(xy_tup)

 
    vtx_sheet = []
    for oid, vtx_list in vtx_dict.iteritems():
        for i, vtx in enumerate(vtx_list):
            vtx_sheet.append((oid, i, vtx[0], vtx[1]))

    writeVerticesToCsv(vtx_sheet)
    writeVerticesToHlg(vtx_sheet)
 
def writeVerticesToCsv(vtx_sheet):
    """Write polygon vertex information to csv"""

    header = (
        'oid',          'sequence_id', 
        'x_coordinate', 'y_coordinate')

    with open(vertex_csv_path, 'wb') as vtx_csv:
        vtx_writer = csv.writer(vtx_csv)
        vtx_writer.writerow(header)

        for row in vtx_sheet:
            vtx_writer.writerow(row)
def writeVerticesToHlg(vtx_sheet):
    """Write polygon vertex information to hlg"""
    outF = open(vertex_hlg_path, "w")
    outF.write('[HIGHLIGHTING]')
    outF.write("\n")
    outF.write('zoom=12')
    count = 0
    for row in vtx_sheet:
        outF.write("\n")
        outF.write('PointLon_'+str(count)+'='+str(row[2]))
        outF.write("\n")
        outF.write('PointLat_'+str(count)+'='+str(row[3]))
        count+=1
    outF.close()
getPolygonCoordinates(polygon_shp)
