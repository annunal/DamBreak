from osgeo import gdal
from osgeo.gdalconst import *
import struct
import sys,os
import numpy as np
from netCDF4 import Dataset

def readGDAL(fname, onlygeoT=False, onlyNDV=False):
    dataset = gdal.Open(fname, GA_ReadOnly )
    geoT=dataset.GetGeoTransform ()
    band = dataset.GetRasterBand(1)
    NoDataValue=band.GetNoDataValue()
    projectionfrom = dataset.GetProjection()
    cellsize=geoT[1]
    if onlygeoT:
        return cellsize,projectionfrom
    if onlyNDV:
        return NoDataValue
    xsize = band.XSize
    ysize = band.YSize
    datatype = band.DataType
    NoDataValue=band.GetNoDataValue()
    #Reading the raster values
    values = band.ReadRaster( 0, 0, xsize, ysize, xsize, ysize, datatype )
    #Conversion between GDAL types and python pack types (Can't use complex integer or float!!)
    data_types ={'Byte':'B','UInt16':'H','Int16':'h','UInt32':'I','Int32':'i','Float32':'f','Float64':'d'}
    #print ('data type: ',gdal.GetDataTypeName(datatype))
    values = struct.unpack(data_types[gdal.GetDataTypeName(datatype)]*xsize*ysize,values)
    #print (np.amin(values),np.amax(values),NoDataValue,cellsize,xsize,ysize)
    
    values1=np.reshape(values,(ysize,xsize))
    values2=np.flipud(values1)
    
    return values2,NoDataValue,cellsize


def extractPoints(batiFile, fdmaxFile, fha, listPoints,outFile):
    print ('reading bati file:',batiFile)
    bati,ndv,cellsize=readGDAL(batiFile)

    print ('opening dataset:',fdmaxFile)
    ncmax= Dataset(fdmaxFile, 'r')
    fdmaxVal=ncmax.variables['FD_MAX'][0]
    print ('extracting lat/lon')
    lons=ncmax.variables['LON'][:]
    lats=ncmax.variables['LAT'][:]
    indices=[]
    fdmax=[]
    for poi in listPoints:
        lon=poi[0]
        lat=poi[1]
        ix=-1
        iy=-1
        for i in range(len(lons)-1):
            #print lons[i],lon, lons[i+1],lon>=lons[i],lon<=lons[i+1]
            if lon>=lons[i] and lon<=lons[i+1]:
                ix=i
                break
        for i in range(len(lats)-1):
            #print lats[i],lat
            if lat>=lats[i] and lat<=lats[i+1]:
                iy=i
                break
        indices.append((ix,iy))
        fdmax.append(fdmaxVal[iy,ix])

    print (indices)
    #a=1/0
    print ('opening dataset:',fha)
    ncha= Dataset(fha, 'r')
    ti=ncha.variables['TIME'][:]
    #ha=ncha.variables['HA'][:]
    values=[]
    for k in range(len(listPoints)):
        ix=indices[k][0]
        iy=indices[k][1]
        try:
          fdm=round(fdmaxVal[iy,ix],1)
        except:
          fdm=-1
        print ('retrieving '+listPoints[k][2]+' '+format(fdm)+' '+format(bati[iy,ix]))
        hv=ncha.variables['HA'][:,iy,ix]+bati[iy,ix]
        values.append(hv)
    ff=open(outFile,'w')
    riga=',,'
    for n in range(len(listPoints)):
        poi=listPoints[n]
        riga += '"lon='+ format(poi[0])+'/lat='+format(poi[1])+'", '
    ff.write(riga+'\n')
    riga='"t (s)","t (h)", '
    for n in range(len(listPoints)):
        ix=indices[n][0]
        iy=indices[n][1]
        try:        
          fdm=round(fdmaxVal[iy,ix],1)
        except:
          fdmax=-1
        poi=listPoints[n]
        riga += poi[2] +'('+format(fdm) +')", '
    ff.write(riga+'\n')

    for it in range(len(ti)):
        riga=format(ti[it])+','+format(ti[it]/3600)+','
        for k in range(len(listPoints)):
            hv=values[k][it]
            riga += format(hv)+','
        ff.write(riga+'\n')
    ff.close()

if __name__ == "__main__":
    print(sys.argv)
    
    fdmaxFile='OUT-EXTREMUM.nc'
    fha='OUT-T-ETA.nc'
    batiFile='outDem.grd'
    gaugeFile='gauges.dat'
    outFile='outTimeline.txt'
    #batiFile='bathymetry_30m_Clip_LARGE.grd'
    for j in range(1,len(sys.argv)-1):
        arg,value=sys.argv[j:j+2]
        print('arg=',arg,'value=',value)
        if arg=='-b':batiFile=value
        if arg=='-g':gaugeFile=value
        if arg=='-m':fdmaxFile=value
        if arg=='-t':FHA=value
        if arg=='-d':dire=value
    
    f=open(dire+os.sep+gaugeFile,'r')
    rows=f.read().split('\n')
    f.close()
    listPoints=[]
    for r in rows[1:]:
        print(r)
        if r !='':
            if ',' in r:
                lat,lon,desc=r.split(',')
            elif ' ' in r:
                lat,lon,desc=r.split(' ')
            lon=float(lon);lat=float(lat)
            listPoints.append((lon,lat,desc))
    print(dire+os.sep+batiFile, dire+os.sep+fdmaxFile, dire+os.sep+fha)
    print(    listPoints)
    extractPoints(dire+os.sep+batiFile, dire+os.sep+fdmaxFile, dire+os.sep+fha, listPoints,dire+os.sep+outFile)