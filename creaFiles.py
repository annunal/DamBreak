import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *

import struct
import os,math

around=[(-1,-1),(-1,0),(-1,1),
        (0,-1) ,        (0,+1),
        (+1,-1),(+1,0),(+1,+1)]
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

def creaLake(fnameDEM,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake,LakeHeight='',simple=2):
   
    print('Opening dem:',fnameDEM)
    cell,proj=readGDAL(fnameDEM,True)
    dem,nodata,xsize,ysize,geoT=readGDAL(fnameDEM)
    print('reshaping file as',xsize,ysize)
    dem1=np.reshape(dem,[ysize,xsize])
    row0,col0=getRowCol(LakePoint,xsize,ysize,geoT)
    print('row col of lake',row0,col0)
    
    if LakeHeight=='':
        dematpoi=dem1[row0,col0]
        deltaLake=0.0
    else:
        dematpoi=dem1[row0,col0]
        deltaLake=LakeHeight-dem1[row0,col0]
    row1,col1=getRowCol(DownDamPoint,xsize,ysize,geoT)
    dematdown=dem1[row1,col1]
    lake=-dematpoi+dem1  #-deltaLake
    #demRiver=dem1.copy()
    print('Lake dem=',dematpoi,'   Downdam dem=',dematdown,  '   Jump=',dematpoi-dematdown)
    print(simple,simple==2,simple==True)
    if simple==True:
        dem2=dem1.copy()
        dem2[dem2==dematpoi]=0.0 #-deltaLake
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
                     dem2[row1,col]=dematdown #+deltaLake
                     lake[row1,col]=deltaLake                     
                  #if dem1[row2,col]==dematpoi:
                  if checkAround(dem1,row2,col,xsize,ysize,dematpoi):
                     dem2[row2,col]=dematdown #+deltaLake
                     lake[row2,col]=deltaLake
               for row in range(row1+1,row2):
                  #if dem1[row,col1]==dematpoi:
                  if checkAround(dem1,row,col1,xsize,ysize,dematpoi):
                     dem2[row,col1]=dematdown #+deltaLake
                     lake[row,col1]=deltaLake
                  #if dem1[row,col2]==dematpoi:
                  if checkAround(dem1,row,col2,xsize,ysize,dematpoi):
                     dem2[row,col2]=dematdown #+deltaLake
                     lake[row,col2]=deltaLake
           dem= dematpoi-dem2 #+deltaLake     
           #row1,col1=getRowCol(DownDamPoint,xsize,ysize,geoT)
           #demRiver=lookAround(dem1,demRiver,row1,col1,xsize,ysize,around)
           #row0,col0=getRowCol(DownDamPoint,xsize,ysize,geoT)  
           #while row0<ysize and row0>0 and col0>0 and col0<xsize:
           #    print(row0,col0,row0<ysize and row0>0 and col0>0 and col0<xsize)
           #    row0,col0=lookMin(dem1,row0,col0,around,demRiver,xsize,ysize)
           #    if demRiver[row0,col0]==-1000:
           #        col0 +=1;row0+=1
           #    else:
           #         demRiver[row0,col0]=-1000
                       
# creazione innesco
    vertix,rect=createRect(LakePoint,DownDamPoint,sizeKM,xsize,ysize,geoT)    
    vertixP=vertix.copy()
    for kk in range(4):
        vertixP[kk]=getRowCol(vertix[kk],xsize,ysize,geoT)
        #dem[vertixP[kk][0],vertixP[kk][1]]=-2000
        #print(vertixP[kk])
    for cou in rect:
        dem[cou[0],cou[1]]=dematpoi-dematdown #+deltaLake
        lake[cou[0],cou[1]]=deltaLake
    CreateGeoTiff(fnameOut,dem,xsize,ysize,geoT,-99999,'GSBG')
    CreateGeoTiff(fnameOutLake,lake,xsize,ysize,geoT,-99999,'GSBG')
    #CreateGeoTiff(fnameOutRiver,demRiver,xsize,ysize,geoT,-99999,'GSBG')
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

#def lookAround(dem,demRiver,row0,col0,xsize,ysize,around):
#    dmax=col0
#    if xsize-col0>dmax:dmax=xsize-col0
#    if row0>dmax: dmax=row0
#    if ysize-row0>dmax: dmax=ysize-row0              
    
#    while row0<ysize and row0>0 and col0>0 and col0<xsize:
#      dmin,row0,col0,found,demRiver=lookMin(dem[row0,col0],dem,row0,col0,around,demRiver,xsize,ysize)      
#      if not found:
#        for delta in range(dmax):
#            if int(delta/100)*100==delta:
#                print('delta, dmax=',delta,dmax)
#            col1=col0-delta
#            col2=col0+delta
#            row1=row0-delta
#            row2=row0+delta
#            if row2>ysize-1: row2=ysize-1
#            if row1<0: row1=0
#            if col2>xsize-1: col2=xsize-1
#            if col1<0: col1=0
        
#            for col in range(col1,col2):
#                dmin,row0,col0,found,demRiver=lookMin(dmin,dem,row1,col,around,demRiver,xsize,ysize)
#                if found and demRiver[row0,col0]!=-1000:
#                    demRiver[row0,col0]=-1000
#                else:
#                    dmin,row0,col0,found,demRiver=lookMin(dmin,dem,row2,col,around,demRiver,xsize,ysize)
#                    if found and demRiver[row0,col0]!=-1000:
#                        demRiver[row0,col0]=-1000
#                    else:
#                        for row in range(row1+1,row2):
#                            dmin,row0,col0,found,demRiver=lookMin(dmin,dem,row,col1,around,demRiver,xsize,ysize)
#                            if found and demRiver[row0,col0]!=-1000:
#                                demRiver[row0,col0]=-1000
#                            else:
#                                dmin,row0,col0,found,demRiver=lookMin(dmin,dem,row,col2,around,demRiver,xsize,ysize)
#                                if found and demRiver[row0,col0]!=-1000:
#                                    demRiver[row0,col0]=-1000
#                                else:
#                                    break
#            if found:
#               break

#    return demRiver
#def lookMin(dmin,dem,r,c,around,demRiver,xsize,ysize):
#    pmin=[dmin,r,c]
#    found=False
#    for cou in around:
#        if r+cou[0]<ysize and r+cou[0]>0 and c+cou[1]>0 and c+cou[1]<xsize:
#           if dem[r+cou[0],c+cou[1]]<pmin[0] and demRiver[r+cou[0],c+cou[1]]!=-1000:
#              pmin=[dem[r+cou[0],c+cou[1]],r+cou[0],c+cou[1]]
#              found=True
#           if dem[r+cou[0],c+cou[1]]==pmin[0]:
#               demRiver[r+cou[0],c+cou[1]]=-2000
            
        
#    return pmin[0],pmin[1],pmin[2],found,demRiver

if __name__ == "__main__":
  #  call example:
  #    creaFiles.py [-s srtm.tif] -w  0.3 -lp 36.32  36.19 -dp 36.12 37.42 [-od outDem.grd]  [-ol outLake.grd ]  [-res newcellsize]
    
    import sys
    args=sys.argv
    fnameDem='srtm.tif'
    fnameOut='outDem.grd'
    fnameOutLake='outLake.grd'
    #fnameOutRiver='outRiver.grd'
    sizeKM=None
    LakePoint=[]
    dire=''
    newCellSize=''
    DownDamPoint=[]
    bbox=''
    LakeHeight=''
    for j in range(len(args)):
        arg=args[j]
        if arg=='-s':
            fnameDem=args[j+1]
        elif arg=='-w':
            sizeKM=float(args[j+1])
        elif arg=='-od':
            fnameOut=args[j+1]
        elif arg=='-ol':
            fnameOutLake=args[j+1]
        #elif arg=='-r':
        #    fnameOutRiver=args[j+1]
        elif arg=='-lp':
            LakePoint=[float(args[j+1]),float(args[j+2])]
        elif arg=='-lh':
            LakeHeight=float(args[j+1])
        elif arg=='-dp':
            DownDamPoint=[float(args[j+1]),float(args[j+2])]
        elif arg=='-d':
            dire=args[j+1]
        elif arg=='-res':
            newCellSize=float(args[j+1])
        elif arg=='-bbox':
            bbox=args[j+1]

                    
    if dire !='':
        fnameDem=dire+os.sep+fnameDem
        fnameOut=dire+os.sep+fnameOut
        fnameOutLake=dire+os.sep+fnameOutLake
        #fnameOutRiver=dire+os.sep+fnameOutRiver
    if sizeKM==None or LakePoint==[] or DownDamPoint==[]:
        print('Error in input data' )
        if sizeKM==None:print('sizeKM not defined , -w xxx')
        if LakePoint==[]:print('LkePoint not defined, -lp  x y')
        if DownDamPoint==[]:print('DownDamPoint not defined, -dp  x y')
        print('syntax: creaFiles.py [-s srtm.tif] -w  0.3 -lp 36.32  36.19 -dp 36.12 37.42 [-od outDem.grd]  [-ol outLake.grd ]  [-bbox xmin ymin xmax ymax')
        quit()
    if not os.path.exists(fnameDem):
        print('Dem file not existing:',fnameDem)
        quit()
    print('*************************************************')
    print('*   Preparation of file for NAMIDANCE DB calc')
    print('*************************************************')
    print('srtm file     =',fnameDem)
    print('Lake Point    =',LakePoint)
    print('Down dam Point=',DownDamPoint)
    print('output DEM    =',fnameOut)
    print('output Lake   =',fnameOutLake)
    #print('delta laake   =',deltaLake)
    #print('output River   =',fnameOutRiver)
    if newCellSize!='' or bbox!='':
        if bbox!='':
	        bb=' -r near -te '+bbox #,str(xmin),str(ymin),str(xmax),str(ymax)])
        else:
            bb=' -r bilinear '
        if newCellSize!='':
           cs=' -tr '+format(newCellSize)+' '+format(newCellSize)
        else:
           cs=''
        fnameDemNew=dire+'/srtmNew.tif'
        print('resizing dem '+fnameDem+' to   = '+format(newCellSize)+'  new file='+fnameDemNew +'  to: '+bbox)
        cmd='gdalwarp '+bb+cs+' '+fnameDem+' '+fnameDemNew
        print(cmd)
        os.system(cmd)
        fnameDem=fnameDemNew
    creaLake(fnameDem,LakePoint,DownDamPoint,sizeKM,fnameOut,fnameOutLake,LakeHeight,2) 
    
    quit()
#Cingoli
#  -d Cingoli -s /data/N43E013.hgt -lp  13.161652  43.382106 -w 0.1 -dp  13.163041  43.384161  -res 0.0001388  -bbox "13.092161  43.343359 13.724455  43.731141"
#Malpasset dam  
#python createFiles.py -d ./Malpasset  -s /data/N43E006.hgt -lp  6.757149  43.51236  -dp  6.757074  43.51192  -lh 100 -bbox 6.67  43.34  6.88 43.57   -res 0.0001388
#Yarseli dam
# python ./creaFiles.py   -d ./Turkey\ EQ/Yarseli\ Dam/case60m -s srtm.tif  -lp 36.327959 36.193402 -dp 36.325398  36.196431 -w 0.06  -od outDem.grd -ol outLake.grd  

#Ataturk dam
# python ./creaFiles.py  -d ./Turkey\ EQ/Ataturk -s srtm.tif  -lp 38.322537  37.483541 -dp 38.314282 37.480067 -w 0.06  -od outDem.grd -ol outLake.grd


#Sultansuyu Dam
# python ./creaFiles.py   -s ./Turkey\ EQ/Sultansuyu\ Dam/srtm.tif  -lp 38.050799 38.318292 -dp 38.052277  38.321512 -w 0.3  -od ./Turkey\ EQ/Sultansuyu\ Dam/outDem.grd -ol ./Turkey\ EQ/Sultansuyu\ Dam/outLake.grd
# 
