from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import struct
import os,math

def dprint(a,b='',c='',d='',e='',f='',g='',h='',i=''):
    debug=False
    debug=True
    if debug:
        print(a,b,c,d,e,f,g,h,i)

def get_angle(p1,p2):
    x1,y1=p1
    x2,y2=p2
    at=math.atan2(y2-y1, x2-x1)
    angle=math.degrees(at)
    return angle
    
def RotatePoint(pPoint, pOrigin, Degrees):
    RotatePoint=[0,0]
    RotatePoint[0] = pOrigin[0] + (math.cos(D2R(Degrees)) * (pPoint[0] - pOrigin[0]) + math.sin(D2R(Degrees)) * (pPoint[1] - pOrigin[1]))
    RotatePoint[1] = pOrigin[1] + (math.sin(D2R(Degrees)) * (pPoint[0] - pOrigin[0]) - math.cos(D2R(Degrees)) * (pPoint[1] - pOrigin[1]))
    return RotatePoint
        
def D2R(Angle):
    pig = 3.1415927
    D2R = Angle / 180* pig
    return D2R
        
def  createRect(p1,p2,sizeKM,xsize,ysize,geoT):  #l, w , p strike )
    p=[(p1[0]+p2[0])/2,(p1[1]+p2[1])/2]
    l=((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
    lon ,lat =p
    vertix0=[0]*4;vertix=[0]*4;vertixP0=[0]*4
    radius = 6340 * math.cos(lat / 180 * 3.1415927)
    w = sizeKM / radius * 180 / 3.1415927
    #l = l / radius * 180 / 3.1415927 
    vertix0[0]=[lon - l / 2, lat - w / 2]
    vertix0[1]=[lon + l / 2, lat - w / 2]
    vertix0[2]=[lon - l / 2, lat + w /2]
    vertix0[3]=[lon + l / 2, lat + w / 2]    
    strike=get_angle(p1,p2)
    for kk in range(4):
        vertix[kk] = RotatePoint(vertix0[kk], p, strike)
        vertixP0[kk]=getRowCol(vertix0[kk],xsize,ysize,geoT)
    rect=[]
    #print(vertixP0)
    
    st=1;
    col0=vertixP0[0][0];col1=vertixP0[2][0]
    if col0>col1: col0,col1=(col1,col0)
    
    print('vv#',col0,col1)
    for col in range(col0*10,col1*10,5):
        col/=10
        row0=vertixP0[0][1];row1=vertixP0[1][1]
        if row0>row1: row0,row1=(row1,row0)
        #print(row0,row1)
        for row in range(row0*10,row1*10,5):
            row /=10
            lon1,lat1=getRowColInv(col,row,xsize,ysize,geoT)
            lon1R,lat1R = RotatePoint((lon1,lat1), p, strike)
            r,c=getRowCol((lon1R,lat1R),xsize,ysize,geoT)
            #print(r,c)
            rect.append((r,c))
    return vertix,rect

        
# see note below
def youCanQuoteMe(item):
        return "\"" + item + "\""

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
    dprint ('data type: ',gdal.GetDataTypeName(datatype))
    values = struct.unpack(data_types[gdal.GetDataTypeName(datatype)]*xsize*ysize,values)
    dprint (np.amin(values),np.amax(values),NoDataValue,cellsize,xsize,ysize)
    return values,NoDataValue,xsize,ysize,geoT

def CreateGeoTiff(FileName, Array, xsize, ysize, GeoT,nodata=99999.0,Gtype='GTiff'):
    DataType = gdal.GDT_Float32
    WKT=  'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'
    driver = gdal.GetDriverByName(Gtype)
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
    band=None
    DataSet=None
    return FileName
    
def getRowCol(poi,xsize,ysize,geoT):
    lon,lat=poi
    cell=geoT[1]
    lonMin=geoT[0]
    lonMax=lonMin+cell*xsize
    latMax=geoT[3]
    latMin=latMax-cell*ysize
    col=int((lon-lonMin)/(cell))
    row=ysize-int((lat-latMin)/(cell))
    return row,col
def   getRowColInv(row,col,xsize,ysize,geoT):
    cell=geoT[1]
    lonMin=geoT[0]
    lonMax=lonMin+cell*xsize
    latMax=geoT[3]
    latMin=latMax-cell*ysize
    lon=col*cell+lonMin
    lat=(ysize-row)*cell+latMin
    return lon,lat
    
def findrows(dem1,dematpoi,row0,col0,ysize,demOut,vout=-1000):
    for row in range(row0,ysize-1):
        if dem1[row,col0]!=dematpoi:            
            break
        else:
            demOut[row,col0]=vout
    rowmax=row
    for row in range(row0,0,-1):
        if dem1[row,col0]!=dematpoi:
            break
        else:
            demOut[row,col0]=vout
    rowmin=row
    return rowmin,rowmax,demOut
def findcols(dem1,dematpoi,row0,col0,xsize,demOut,vout=-1000):
    for col in range(col0,xsize-1):
        if dem1[row0,col]!=dematpoi:
            break
        else:
            demOut[row0,col]=vout
    colmax=col
    for col in range(col0,0,-1):
        if dem1[row0,col]!=dematpoi:
            break
        else:
            demOut[row0,col]=vout                
    colmin=col
    return colmin,colmax,demOut

def creaLake(fnameDEM,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake,simple=False):
    print('Opening dem:',fnameDEM)
    cell,proj=readGDAL(fnameDEM,True)
    dem,nodata,xsize,ysize,geoT=readGDAL(fnameDEM)
    print('reshaping file as',xsize,ysize)
    dem1=np.reshape(dem,[ysize,xsize])
    row0,col0=getRowCol(LakePoint,xsize,ysize,geoT)
    print('row col of lake',row0,col0)
    dematpoi=dem1[row0,col0]
    row1,col1=getRowCol(DownDamPoint,xsize,ysize,geoT)
    dematdown=dem1[row1,col1]
    lake=-dematpoi+dem1
    
    print('Lake dem=',dematpoi,'   Downdam dem=',dematdown,  '   Jump=',dematpoi-dematdown)
    print(simple,simple==2,simple==True)
    if simple==True:
        dem2=dem1.copy()
        dem2[dem2==dematpoi]=0.0
        dem= dematpoi-dem2
        #lake=-dematpoi+dem1
        #CreateGeoTiff(fnameOut,dem,xsize,ysize,geoT,-99999,'GSAG')
        #CreateGeoTiff(fnameOutLake,lake,xsize,ysize,geoT)
    else:
        if simple==0:
          dem2=dem1.copy()
          rowmin,rowmax,dem2=findrows(dem1,dematpoi,row0,col0,ysize,dem2)    
          print(rowmin,rowmax)
          for row in range(rowmin,rowmax):
              if int(row/10)*10==row:
                  print(row, format(int((row-rowmin)/(rowmax-rowmin)*100))+'%')
              colmin1,colmax1,dem2=findcols(dem1,dematpoi,row,col0,xsize,dem2,dematdown)        
              for col in range(colmin1,colmax1):    
                  rowmin1,rowmax1,dem2=findrows(dem1,dematpoi,row,col,ysize,dem2,dematdown)
                  for row2 in range(rowmin1,rowmax1):
                      colmin2,colmax2,dem2=findcols(dem1,dematpoi,row2,col,xsize,dem2,dematdown)   
          
          dem= dematpoi-dem2
        elif simple==2:
        # cornici
           dmax=col0
           if xsize-col0>dmax:dmax=xsize-col0
           if row0>dmax: dmax=row0
           if ysize-row0>dmax: dmax=ysize-row0           
           dem2=dem1.copy()
           for delta in range(1,dmax):
               if int(delta/100)*100==delta:
                 print('delta, dmax=',delta,dmax)
               col1=col0-delta
               col2=col0+delta
               row1=row0-delta
               row2=row0+delta
               if row2>ysize-1: row2=ysize-1
               if row1<0: row1=0
               if col2>xsize-1: col2=xsize-1
               if col1<0: col1=0
               
               for col in range(col1,col2):
                  #if dem1[row1,col]==dematpoi:
                  if checkAround(dem1,row1,col,xsize,ysize,dematpoi):
                     dem2[row1,col]=dematdown
                  #if dem1[row2,col]==dematpoi:
                  if checkAround(dem1,row2,col,xsize,ysize,dematpoi):
                     dem2[row2,col]=dematdown
               for row in range(row1+1,row2):
                  #if dem1[row,col1]==dematpoi:
                  if checkAround(dem1,row,col1,xsize,ysize,dematpoi):
                     dem2[row,col1]=dematdown
                  #if dem1[row,col2]==dematpoi:
                  if checkAround(dem1,row,col2,xsize,ysize,dematpoi):
                     dem2[row,col2]=dematdown
           dem= dematpoi-dem2     
               
                       
# creazione innesco
    vertix,rect=createRect(LakePoint,DownDamPoint,sizeKM,xsize,ysize,geoT)    
    vertixP=vertix.copy()
    for kk in range(4):
        vertixP[kk]=getRowCol(vertix[kk],xsize,ysize,geoT)
        #dem[vertixP[kk][0],vertixP[kk][1]]=-2000
        #print(vertixP[kk])
    for cou in rect:
        dem[cou[0],cou[1]]=dematpoi-dematdown
        lake[cou[0],cou[1]]=0.0
    CreateGeoTiff(fnameOut+'.grd',dem,xsize,ysize,geoT,-99999,'GSBG')
    CreateGeoTiff(fnameOutLake+'.grd',lake,xsize,ysize,geoT,-99999,'GSBG')
    #CreateGeoTiff(fnameOut+'.tif',dem,xsize,ysize,geoT,-99999,'GTiff')
    #CreateGeoTiff(fnameOutLake+'.tif',lake,xsize,ysize,geoT,-99999,'GTiff')

def checkAround(dem,r,c,xs,ys,vin):
    if dem[r,c] !=vin:
       return False
    if r+1<ys and c+1<xs and r>1 and c>1:
        if dem[r+1,c-1]!=vin or dem[r+1,c]!=vin or dem[r+1,c+1]!=vin:
            return False
        if dem[r-1,c-1]!=vin or dem[r-1,c]!=vin or dem[r-1,c+1]!=vin:
            return False
        if dem[r,c-1]!=vin or dem[r,c+1]!=vin:
            return False
    #print(r,c,True)
    return True
        
        
#Yarseli dam
dire='./Turkey EQ/Yarseli Dam/case60m/'
LakePoint=[36.327959,  36.193402]  #dam lake
#LakePoint=[ 36.321174 , 36.19380]
#DownDamPoint=[36.327959,  36.195398] 
DownDamPoint=[ 36.325398,  36.196431]
sizeKM=0.06
fnameDEM=dire+'srtm.tif'
fnameOut=dire +'outDem'
fnameOutLake=dire +'outLake' 
creaLake(fnameDEM,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake,2) 

#Ataturk dam
dire='./Turkey EQ/Ataturk/'
LakePoint   =[ 38.322537,  37.483541]  #dam lake
DownDamPoint=[ 38.314282 , 37.480067] 
sizeKM=0.3
fnameDEM=dire+'srtm.tif'
fnameOut=dire +'outDem'
fnameOutLake=dire +'outLake' 
#creaLake(fnameDEM,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake,2) 


#Sultansuyu Dam
dire='./Turkey EQ/Sultansuyu Dam/'
LakePoint=[  38.050799, 38.318292]  #dam lake
DownDamPoint=[  38.052277,  38.321512] 
sizeKM=0.3
fnameDEM=dire+'srtm.tif'
fnameOut=dire +'outDem'
fnameOutLake=dire +'outLake' 
#creaLake(fnameDEM,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake)
