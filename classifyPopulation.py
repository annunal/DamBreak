#! /usr/bin/python
#! /usr/bin/python
#  0.  read the charactristics of the input file
#  1.  extract a piece of landscan corresponding to the required bounding box
#  2.  resample the vmax file to the resolution of landscan
#  3.  classify the vmax file creating another array of values classified
#  4.  count the popolation in each cell and assign to the class
#  5.  print( output

from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import struct
import sys
import subprocess
import os
import pandas
#import pp
#from classValue import *
#from classifyPP import classValues


gdalwarp="gdalwarp"  #/share/apps/GDAL/bin/gdalwarp"


#srcNDV='-32768'

countriesFile="/mnt/DISKD/DAM_BREAK/DATA/countries.tif"
countryTable='/mnt/DISKD/DAM_BREAK/DATA/Landscan_ISO.csv'

def readCountries():
    points=pandas.read_csv(countryTable,delimiter=',')
    ids,countries,iso3=points['VALUE'][:],points['COUNTRY'][:] ,points['ISO_3'][:]
    return ids,countries,iso3

#=============================================================================================================
def dprint(a,b='',c='',d='',e='',f='',g='',h='',i=''):
    debug=False
    #debug=True
    if debug:
        print(a,b,c,d,e,f,g,h,i)

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
    
    return values,NoDataValue
    
def classValues(claMin,claMax,values,popDensValues,countryValues,NDV,NoDataValue,NoDataValueC,n0,n1):
    maxValueWatHei=-1
    classification_countries = [[] ,[],[] , [], [], [], []]
    popcountries=[]
    popvalues=[0,0,0,0,0,0,0]
    print ('in PP classifying ',n0,n1)
    for cell in range(n0,n1):
        #print 'n0,n1',n0,n1,'cell=',cell
        
        try:
            cl=popDensValues[cell]
            value=values[cell]
            cind=countryValues[cell]
            if not cind==NoDataValueC:
                cou=cind
                #cou=countries[cind-1]
                #dprint (cind,cou)
            else:
                cou=-1
                #cou=''
                
        except:
            print (cell,len(popDensValues),len(values))
            sys.exit()
        #for cl_value in claMin:
        #print 'analysing'
        if cl>0:
            for index in range(0,len(claMin)):
                    
                if value > claMin[index] and value<=claMax[index] and (not cl==NoDataValue) and (not value==NDV):
                    if value>maxValueWatHei:
                        maxValueWatHei=value
                    
                    #if cl_value>1:
                    #    print "index=",index,"cell=",cell, "value=", value,"cl_value=",cl_value
                    # values1[cell]=classification_output_values[index]
                    try:
                        if cell<len(popDensValues):
                            popvalues[index]=popvalues[index]+cl
                            if (not cou in classification_countries[index]) and (cou != -1):
                                classification_countries[index].append(cou)
                            
                            if len(popcountries)>0:        
                                t=[]
                                for k in popcountries:
                                    t.append(k[0])
                                if not cou in t:
                                    popcountries.append([cou,[0,0,0,0,0,0,0]])
                            else:
                                popcountries.append([cou,[0,0,0,0,0,0,0]])
                            
                            for courow in popcountries:
                                if cou==courow[0]:
                                    courow[1][index] +=cl
                            
                                
                        break
                    except:
                        print ("index=",index,"cell=",cell)
                        print ("Unexpected error:", sys.exc_info()[0])
                        raise
                    
                #cl_value0=cl_value
                #index = index + 1
        #print cell, values[cell],classification_output_values[index]
        #cell = cell +1
    res=[n0,n1,maxValueWatHei,classification_countries,popvalues,popcountries]
    return res
        
def classFile(u10maxFile,pwd, desc, outxml,PopulationDensityBaseFile,PopFileDesc,suffix='',factor=1):

    maxValueWatHei1=-1
    maxValueWatHei2=-1
    maxValueWatHei3=-1
    
    claMin=[0,  0.2,   2.5, 5., 10., 20.]   #The interval values to classify
    claMax=[0.2, 2.5,   5., 10., 20., 1000] #The interval values to classify

    claMin=[0,  0.05,   1, 3., 10., 20.]   #The interval values to classify
    claMax=[0.05, 1,   3., 10., 20., 1000] #The interval values to classify
    
    #classification_values =        [0,  33, 42.7, 50, 58, 70, 1000] #The interval values to classify
    #classification_output_values = [128, 0 , 1,   2 , 3,  4, 5] #The value assigned to each interval
    
    classification_output_labels = ["0-0.2" ,"0.2-2.5","2.5-5." , "5.-10.", "10.-20.", ">20.", ""] #The value assigned to each interval
    classification_output_labels = ["0-0.05" ,"0.05-1","1-3" , "3-10.", "10.-20.", ">20.", ""] #The value assigned to each interval
    classification_output_ranges = ["" ,"","" , "", "", "", ""]
    classification_countries = ["" ,"","" , "", "", "", ""]
    popvalues=[0,0,0,0,0,0,0]
    popcountries=[]
    
    # Syntax:  classify.py  u10filename  fileOutClassified   workdir


    popdensity_file=pwd+os.sep+"popfile_clipped.tif"
    country_file0=pwd+os.sep+"countryfile_clipped0.tif"
    country_file=pwd+os.sep+"countryfile_clipped.tif"

    print ('Input file: ', u10maxFile)
    print ('PopFile: ', popdensity_file)
    print ('country: ', country_file)

    #Opening the raster file
    if not os.path.exists(u10maxFile):
        print ('file not existing ',u10maxFile)
        sys.exit()
    else:
        dprint ('reading ',u10maxFile)
        
    if not os.path.exists(PopulationDensityBaseFile):
        print ('file not existing ',PopulationDensityBaseFile)
        sys.exit()
    
    if os.path.exists(popdensity_file):
        os.remove(popdensity_file)
    
    if os.path.exists(country_file):
        os.remove(country_file)
    if os.path.exists(country_file0):
        os.remove(country_file0)
    
    # get the cellsize of pop density file
    popCellSize,proj=readGDAL(PopulationDensityBaseFile,True)
    print ('popCellSize=',popCellSize)
    print ('projection=',proj)
    if 'Mollweide' in proj:  
        Moll=True
        #t_srs='-t_srs "+proj=moll +lon_0=0 +a=1737400 +b=1737400 +no_defs"'
        t_srs='-t_srs "+proj=moll +lon_0=0 +datum=WGS84 +a=6378137 +b=298.257223563 +no_defs"'
    else:
        Moll=False
        t_srs=''
    
    #-------------------------------------------------------------------------------
    #  1.  resample the vmax file to the resolution of landscan
    #-------------------------------------------------------------------------------
    dprint ("")
    dprint ("-------------------------------------------------------------------------------")
    print (">>  1.  resample the vmax file to the resolution and proj of pop density ", popCellSize,' deg')
    dprint ("-------------------------------------------------------------------------------")

    # resmaple as population
    cmd="-r bilinear -tr " + str(popCellSize) +" " + str(popCellSize)+ " " +t_srs
    
    raster_file=pwd+os.sep+"u10res.tif"

    try:
        os.remove(raster_file)
    except OSError:
        pass    

    fullCmd=' '.join([gdalwarp,cmd,youCanQuoteMe(u10maxFile),youCanQuoteMe(raster_file)])
    dprint(fullCmd +'>>'+pwd+os.sep+'logwarp.txt')
    os.system(fullCmd +'>>'+pwd+os.sep+'logwarp.txt')

    #-------------------------------------------------------------------------------
    #  2.  read the charactristics of the input file
    #-------------------------------------------------------------------------------
    dprint ("-------------------------------------------------------------------------------")
    print (">>  2.  read the charactristics of the input file")
    dprint ("-------------------------------------------------------------------------------")

    u10dataset = gdal.Open(raster_file, GA_ReadOnly )
    u10band = u10dataset.GetRasterBand(1)
    #Reading the raster properties
    u10projectionfrom = u10dataset.GetProjection()
    u10geotransform = u10dataset.GetGeoTransform()
    ncols = u10band.XSize
    nrows = u10band.YSize
    # get raster georeference info
         
    xmin = u10geotransform[0]
    ymax = u10geotransform[3]
    pixelWidth = u10geotransform[1]
    pixelHeight = u10geotransform[5]

    xmax=xmin+ncols*pixelWidth
    ymin=ymax+nrows*pixelHeight

    dprint (xmin, xmax, ymin, ymax)


    
    #-------------------------------------------------------------------------------
    #  3.  extract a piece of pop Densoty file corresponding to the required bounding box
    #-------------------------------------------------------------------------------
    dprint ("")
    dprint ("-------------------------------------------------------------------------------")
    print (">>  3.  extract a piece of landscan corresponding to the required bounding box")
    dprint ("-------------------------------------------------------------------------------")

    
    cmd=' '.join([" -te ",str(xmin),str(ymin),str(xmax),str(ymax)])
    fullCmd=gdalwarp+' '+' '.join([cmd,youCanQuoteMe(PopulationDensityBaseFile),youCanQuoteMe(popdensity_file)])
    
    dprint (fullCmd)
    os.system(fullCmd +'>>'+pwd+os.sep+'logwarp.txt')

    #-------------------------------------------------------------------------------
    #  3a.  extract a piece of countries corresponding to the required bounding box and proj to popDensity
    #-------------------------------------------------------------------------------
    dprint ("")
    dprint ("-------------------------------------------------------------------------------")
    print (">>  3a.  extract a piece of countries corresponding to the required bounding box and resolution/proj of pop density")
    dprint ("-------------------------------------------------------------------------------")

    # cut population file
    #try:
    #    os.remove(popDensityFile)
    #except OSError:
    #    pass    

    cmd=' '.join(["-r near -tr " + str(popCellSize) +" " + str(popCellSize),t_srs,"-te ",str(xmin),str(ymin),str(xmax),str(ymax)])
    fullCmd=' '.join(["gdalwarp",cmd,youCanQuoteMe(countriesFile),youCanQuoteMe(country_file)])
    dprint (fullCmd)
    os.system(fullCmd +'>>'+pwd+'logwarp.txt')
    
    
    #gdalwarp -te $xmin $ymin $xmax $ymax /mnt/modelling/local/development1/DATA/lspop20141.tif  lspop20141_clipped.tif
    #-------------------------------------------------------------------------------
    #  4.  classify the vmax file creating another array of values classified
    #-------------------------------------------------------------------------------
    dprint ("")
    dprint ("-------------------------------------------------------------------------------")
    print (">>  4.  classify the vmax file creating another array of values classified")
    dprint ("-------------------------------------------------------------------------------")

        
    values0,NDV=readGDAL(raster_file)
    popDensValues0,NoDataValue=readGDAL(popdensity_file)
    countryValues0,NoDataValueC=readGDAL(country_file)
        
    values1=np.array(values0)/factor
    popDensValues1=np.array(popDensValues0)
    countryValues1=np.array(countryValues0)
    maxValueWatHei1=np.amax(values1[values1 != NDV])
    
    ids,countries,isocodes=readCountries()
    
    dprint (np.shape(values1),np.shape(popDensValues1),np.shape(countryValues1))
        
    cond=(popDensValues1>0) & (popDensValues1!=NoDataValue) & (values1>claMin[0])
    dprint ( cond.shape,np.amax(cond))
    
    totPop=np.sum(popDensValues1[popDensValues1!=NoDataValue])
    dprint ('file ',popdensity_file, ' total sum pixels=',totPop/1e6, ' million')

    values=values1[cond]
    popDensValues=popDensValues1[cond]
    countryValues=countryValues1[cond]
    
    totPop=np.sum(popDensValues)
    print ('file ',popdensity_file, ' v>vmin sum pixels=',totPop/1e6, ' million')
    dprint (values.shape,np.shape(popDensValues),np.shape(countryValues))
    
    if len(values)>0:
        maxValueWatHei2=np.amax(values)
        #-------------------------------------------------------------------------------
        #  5.  count the popolation in each cell and assign to the class and write to output
        #-------------------------------------------------------------------------------
        dprint ("")
        dprint ("-------------------------------------------------------------------------------")
        print (">>  5.  count the popolation in each cell and assign to the class and write to output")
        dprint ("-------------------------------------------------------------------------------")

        parallel=False
        for index in range(0,len(claMin)):
                classification_output_ranges[index]="WatHei>"+str(claMin[index])+" and <="+str(claMax[index])
            
        if parallel:
            # # Create jobserver
            # print( 'preparing PP server'
            # job_server = pp.Server()
            nint=10
            # dprint ('setting jobs')
            # job_server.set_ncpus(nint)
            # dprint ('end setting jobs')
            # jobs = []

            
            # maxValueWatHei=-1
            # results=[]
            # dprint ('start with ', job_server.get_ncpus())
            
            # for n0 in range(0,len(values),len(values)/nint):
                
                # n1=n0+len(values)/nint-1
                
                # if n1>len(values): n1=len(values)
                # dprint ('n0=',n0,n1)
                # jobs.append(job_server.submit(classValues, (claMin,claMax,values,popDensValues,countryValues,NDV,NoDataValue,NoDataValueC,n0,n1)))
            
            # job_server.wait()
            # maxValueWatHei=-1
            # for job in jobs:
                # dprint (job())
                # #for res in job():
                # #    print np.shape(res)
                # #    print res
                # res=job()
                # n0=res[0]
                # n1=res[1]
                # mx=res[2]
                # if mx>maxValueWatHei: maxValueWatHei=mx
        
                # classification_countriesX=res[3]
                # popvaluesX=res[4]
                # #print n0, classification_countriesX
                # for index in range(0,len(claMin)):
                    # popvalues[index]+=popvaluesX[index]
                    # for couIndex in classification_countriesX[index]:
                        # cou=countries[couIndex-1]
                        # dprint (index,cou)
                        # if not cou in classification_countries[index]:
                            # if not classification_countries[index]=='':
                                # classification_countries[index] += ', '
                            # classification_countries[index] +=cou
                    
        else:
            n0=0
            n1=values.shape[0]
            res=classValues(claMin,claMax,values,popDensValues,countryValues,NDV,NoDataValue,NoDataValueC,n0,n1)
            maxValueWatHei3=res[2]
            popvalues=res[4]
            classification_countriesX=res[3]
            popcountries=res[5]
            for index in range(0,len(claMin)):
                for couIndex in classification_countriesX[index]:
                        cou=countries[couIndex-1]
                        if not cou in classification_countries[index]:
                            if not classification_countries[index]=='':
                                classification_countries[index] += ', '
                            classification_countries[index] +=cou
    
    # --- new ---
    if maxValueWatHei1>300: maxValueWatHei1=-1
    if maxValueWatHei2>300: maxValueWatHei2=-1
    if maxValueWatHei3>300: maxValueWatHei3=-1
    ValueALL=[maxValueWatHei1,maxValueWatHei2,maxValueWatHei3]
    maxValueWatHei=np.max(ValueALL)
    #-------------------------------------------------------------------------------
    #  6.  print( output
    #-------------------------------------------------------------------------------
    #outxml=pwd+'popDensValues'+suffix +'.xml'
    dprint ("")
    dprint ("-------------------------------------------------------------------------------")
    print (">>  6.  print( output in ",outxml)
    dprint ("-------------------------------------------------------------------------------")
    
    
    out_xml=open(outxml,"w")
    out_xml.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<popvalues MaxValueWatHei=\"'+str(maxValueWatHei)+'\" unit="m" >\n')
    out_xml.write("<!-- "+desc+"  -->\n")
    out_xml.write("<!-- "+PopulationDensityBaseFile+"  -->\n")
    out_xml.write("<!-- "+PopFileDesc+"  -->\n")
    zeroToSix=range(0,6)
    for index in zeroToSix:
        print (classification_output_labels[index],int(popvalues[index]),"("+classification_output_ranges[index]+") "+ classification_countries[index])
        testo="\t<class>\n"
        testo +="\t\t<value><![CDATA["+classification_output_ranges[index]+"]]></value>\n"
        testo +="\t\t<ListCountries>"+classification_countries[index]+"</ListCountries>\n"
        testo +="\t\t<category>"+str(classification_output_labels[index])+"</category>\n"
        testo +="\t\t<popValue>"+str(int(popvalues[index]))+"</popValue>\n"
        
        if len(popcountries)>0 and int(popvalues[index])>0:
            testo +="\t\t<countriesPop>\n"
            for courow in popcountries:
                #print courow
                #print index,courow[1][index]
                if courow[0]==-1:
                    cou='Other countries'
                    iso=''
                else:
                    cou=countries[courow[0]-1]
                    iso=isocodes[courow[0]-1]
                
                testo +="\t\t\t<country name=\""+cou+"\" iso3=\""+iso+"\">"+str(int(courow[1][index]))+"</country>\n"
            testo +="\t\t</countriesPop>\n"    
        else:
            testo +="\t\t<countriesPop/>\n"    
        testo +="\t</class>\n"
        
        out_xml.write(testo)
        print (testo)
    out_xml.write("</popvalues>")
    out_xml.close()
    
    return outxml



    #os.remove(popdensity_file)                                 

if __name__ == "__main__":
    arguments = sys.argv[1:]

    u10maxFile='' #FD_MAX_30m.tif'
    dir='./' 
    #desc='Kyev reservoir'
    #desc='Mozambique'
    desc='case'
    ncf=False
    pop='LS'
    for j in range(1,len(sys.argv)-1):
        arg,value=sys.argv[j:j+2]
        print('arg=',arg,'value=',value)
        if arg=='-d':dir=value
        if arg=='-desc':desc=value
        if arg=='-fm':u10maxFile=value
        if arg=='-nc':ncf=True
        if arg=='-p':pop=value
    if pop=='LS':
        PopulationDensityBaseFile="/mnt/DISKD/DAM_BREAK/DATA/lspop20141.tif"
        PopFileDesc="LANDSCAN 2014"
        #popCellsize="0.008333333333333"
    elif pop=='GHSL':
    #srcNDV=''
        #https://ghsl.jrc.ec.europa.eu/download.php?ds=pop to download this file and then 
        #choose 1 km resolution, Mollweide
        #PopulationDensityBaseFile="/mnt/DISKD/DAM_BREAK/DATA/GHS_POP_GPW42015_GLOBE_R2015A_54009_250_v1_0.tif"
        #popCellsize="0.001248439450687"
        PopulationDensityBaseFile="/mnt/DISKD/DAM_BREAK/DATA/GHS_POP_E2015_GLOBE_R2019A_4326_30ss_V1_0.TIF"
        PopFileDesc="GHSL JRC"
        #popCellsize="0.008333333333333"

    if ncf:
        cmd='gdal_translate -ot Float64  NETCDF:'+dir+os.sep+'OUT-EXTREMUM.nc:FD_MAX -b 1 -unscale  '+dir+os.sep+'FD_MAX.tif'
        u10maxFile=dir+os.sep+'FD_MAX.tif'
        print(cmd)
        os.system(cmd)

    outxml=dir+os.sep+'outClassify_'+pop+'.xml'
    classFile(u10maxFile,dir, desc,outxml,PopulationDensityBaseFile,PopFileDesc,'',1)

