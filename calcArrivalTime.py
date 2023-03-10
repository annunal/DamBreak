from osgeo import gdal
from osgeo.gdalconst import *
import sys,os

import numpy as np
from netCDF4 import Dataset
fdmaxFile='OUT-EXTREMUM.nc'
fha='OUT-T-ETA.nc'

#  call example:
#    creaFiles.py [-s srtm.tif] -w  0.3 -lp 36.32  36.19 -dp 36.12 37.42 [-od outDem.grd]  [-ol outLake.grd ]  [-res newcellsize]

def CreateGeoTiff(FileName, Array, xsize, ysize, GeoT,nodata=99999.0):
    try:
        DataType = gdal.GDT_Float32
        WKT=  'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'
        
        driver = gdal.GetDriverByName('GTiff')
        print('creating dataset')
        # Set up the dataset
        DataSet = driver.Create( FileName, xsize, ysize, 1, DataType )
                # the '1' is for band 1.
        print (GeoT)
        DataSet.SetGeoTransform(GeoT)
        DataSet.SetProjection( WKT )
        # Write the array
        print (xsize,ysize,np.shape(Array))
        band=DataSet.GetRasterBand(1)
        band.SetNoDataValue(nodata)
        band.WriteArray( Array )
        return FileName
    except Exception as e:
        print('error ',e)
        
import sys
args=sys.argv
dire=''
hmin=0.05
step=5

for j in range(len(args)):
    arg=args[j]
    if arg=='-d':
        dire=args[j+1]
    if arg=='-h':
        hmin=float(args[j+1])
    if arg=='-s':
        step=int(args[j+1])
        
print( 'opening dataset:',dire+os.sep+fdmaxFile)
ncmax= Dataset(dire+os.sep+fdmaxFile, 'r')

print ('extracting lat/lon')
lons=ncmax.variables['LON'][:]
lats=ncmax.variables['LAT'][:]
fdmax=ncmax.variables['FD_MAX'][:]
print (len(lons))
indices=np.where((fdmax>hmin) & (fdmax<1000))
nvalues=np.shape(indices)[1]
print ('nvalues>'+format(hmin)+'=',nvalues,'\n')

print ('opening dataset:',fha)
ncha= Dataset(dire+os.sep+fha, 'r')
ti=ncha.variables['TIME'][:]
#ha=ncha.variables['HA'][:]
ha0=ncha.variables['HA'][0]
iy0=indices[1]
ix0=indices[2]

tarr=np.zeros((len(lats), len(lons)))
tarr.fill(-1)
fa=open(dire+os.sep+'tarrival.XYZ','w')
fa.write('lon,lat,tarr (h)\n')

for it in range(len(ti)):
    ha=ncha.variables['HA'][it]
    if int(it/100)*100==it:
        print(it,round(ti[it]/3600.0,1))
    for i in range(0,len(ix0),step):
        ix=ix0[i]
        iy=iy0[i]
        hv=ha[iy,ix]-ha0[iy,ix]
        if hv>0.05 and tarr[iy,ix]==-1:
            tarr[iy,ix]=ti[it]/3600.0
            
fa=open(dire+os.sep+'tarrival.txt','w')
fa.write('lon,lat,tarr (h)\n')
for i in range(0,len(ix0),step):
    ix=ix0[i]
    iy=iy0[i]
    fa.write(format(lons[ix])+','+format(lats[iy])+','+format(tarr[iy,ix])+'\n')
fa.close()

print(len(lats),len(lons))
#fa=open(dire+os.sep+'tarrival.XYZ','w')
#fa.write('lon,lat,tarr (#h#)\n')
#for ix in range(6013):
#    for iy in range(6121):
#        fa.write(format(lons[ix])+','+format(lats[iy])+','+format(tarr[iy,ix])+'\n')
#fa.close()


# for ix in range(0,len(lons),5):
    # if int(ix/250)*250==ix:
        # print ix,len(lons)
    # for iy in range(0,len(lats),5):
        # if ha[0,iy,ix]==ha[len(ti)-1,iy,ix]:
            # tarr[iy,ix]=-1    
        # else:
            # for it in range(len(ti)):
                # hv=ha[it,iy,ix]-ha[0,iy,ix]
                # if hv>0.2:
                    # tarr[iy,ix]=ti[it]/3600.0
                    # fa=open('tarrival.XYZ','a')
                    # fa.write(format(lons[ix])+','+format(lats[iy])+','+format(tarr[iy,ix])+'\n')
                    # fa.close()
                    # break

                    
                    # # for i in range(nvalues):

    # arrivalTime=-1
    # for it in range(len(ti)):
        # hv=ha[it,iy[i],ix[i]]-ha[0,iy[i],ix[i]]
        # #print it,hv,hv>0.2
        # if hv>0.2:
            # #print 'found'
            # arrivalTime=ti[it]/3600.
            # break
            
    # #print 'Arrival time=',arrivalTime
    # tarr[iy[i],ix[i]]=arrivalTime
    # fa=open('tarrival.XYZ','a')
    # fa.write(format(lons[ix[i]])+','+format(lats[iy[i]])+','+format(arrivalTime)+'\n')
    # fa.close
    # if (int(i/10000)*10000==i):
        # print i,arrivalTime,format(i/nvalues*100.)+'%'
        
print ('preparing gTiff')
xsize=len(lons)
ysize=len(lats)
dlon=lons[1]-lons[0]
dlat=lats[1]-lats[0]
if lons[0]>180:
    GeoT=[lons[0]-360,dlon,0,lats[0],0, dlat]
else:
    GeoT=[lons[0],dlon,0,lats[0],0, dlat]

try:
    print (CreateGeoTiff(dire+os.sep+'tarrHours.tif',tarr,xsize,ysize,GeoT,99999.0)        )
except Exception as e:
    print ('error in procedure',e)

    
