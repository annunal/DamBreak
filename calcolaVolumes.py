from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import struct,os
import sys

import numpy as np
from netCDF4 import Dataset

def findValue(array,value):
	f=0
	indices = [] 
	for index, item in enumerate(array):    
		if item ==value:
			indices.append(index) 
	return indices


	
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

#gdal_translate -of GTIFF NETCDF:"OUT-EXTREMUM.nc:FD_MAX" fdmax.tif

lakeFile='outLake.grd'
batiFile='outDem.grd'
#
valLake=0.0

#fmax='OUT-EXTREMUM.nc'
fha='OUT-T-ETA.nc'

print ('reading lake file:',lakeFile)
#====================================
lakeRaster,ndv,cellsize=readGDAL(lakeFile)
print ('reading bati file:',lakeFile)
bati,ndv,cellsize=readGDAL(batiFile)
print (np.max(lakeRaster),np.min(lakeRaster),np.shape(lakeRaster))

#print lakeRaster
cellsizeM=2*3.1415927 * 6370000 * cellsize/360

print ('opening dataset:',fha)
#====================================
ncha= Dataset(fha, 'r')
ti=ncha.variables['TIME'][:]
ha=ncha.variables['HA'][:]
print ('extracting lat/lon')
lons=ncha.variables['LON'][:]
lats=ncha.variables['LAT'][:]

#====================================
# reshape the lake raster

#lakeRaster=lakeRasterV.reshape(lon(lons),len(lats))
print (np.shape(ha),np.shape(lakeRaster))

print ('extracting cells with value ', valLake)
indices=np.where(lakeRaster==valLake)
#indices=findValue(lakeRaster,valLake)
print (np.shape(indices))
#nvalues=np.shape(indices)[0]
nvalues=np.shape(indices)[1]
print ('nvalues=',nvalues,'\n')

#sys.exit()

#print ('opening dataset:',fmax
#ncmax= Dataset(fmax, 'r')

#fdmax=ncmax.variables['FD_MAX'][:]

#indices=np.where(fdmax>0.2)

iy=indices[0]
ix=indices[1]

#tarr=np.zeros((len(lats), len(lons)))
#tarr.fill(-1)
sum0=0
t0=0
for it in range(len(ti)):
	sum=0
	hmed=0
	for i in range(nvalues):
		hv=bati[iy[i],ix[i]]+ha[it,iy[i],ix[i]]
		sum +=hv*cellsizeM*cellsizeM
		hmed +=hv/nvalues
		if it>0:
			mflow=-(sum-sum0)/(ti[it]-t0)
		else:
			mflow=0
	print ti[it],ti[it]/3600.,sum,sum/1.e6,mflow,hmed
	sum0=sum
	t0=ti[it]

	
def CreateGeoTiff(FileName, Array, xsize, ysize, GeoT,nodata=99999.0):
    DataType = gdal.GDT_Float32
    WKT = "GEOGCS[""WGS 84"",DATUM[""WGS_1984"",SPHEROID[""WGS 84"",6378137,298.2572235629972,AUTHORITY[""EPSG"",""7030""]],AUTHORITY[""EPSG"",""6326""]],PRIMEM[""Greenwich"",0],UNIT[""degree"",0.0174532925199433],AUTHORITY[""EPSG"",""4326""]]"
    driver = gdal.GetDriverByName('GTiff')
    # Set up the dataset
    DataSet = driver.Create( FileName, xsize, ysize, 1, DataType )
            # the '1' is for band 1.
    #print GeoT
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( WKT )
    # Write the array
    #print xsize,ysize,np.shape(Array)
    band=DataSet.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.WriteArray( Array )
    return FileName

