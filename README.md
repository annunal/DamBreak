# DamBreak
Dambreak sowftare tools


Install conda, then create an environment  called gdal
conda create -n gdal
conda install gdal




To run use this command:
creaFiles.py [-d basedir] [-s srtm.tif] -w  0.3 -lp 36.32  36.19 -dp 36.12 37.42 [-od outDem.grd]  [-ol outLake.grd ]  [-bbox xmin ymin xmax ymax] [-res NewCellSize]

where:
-d <dir>:  is the base directory. If is not specified the current directory is used
-s <fname>:  is the SRTM file that is used [default:  srtm.tif]
-w <sizeKM>:
-lp <lon lat>:
-dp <lon lat> 
-od <output dem grid>
-ol <output Lake grid>:
-bbox <xmin ymin xmax ymax>
-res <NewCellSize>


Example: Cingoli dam break
![wholeLake](https://user-images.githubusercontent.com/10267112/218803450-b19dd755-7849-4dbd-8264-bc1da0de5dc0.png)
The Cingoli dam is located in Italy, Marche region.

Identify the dedicated SRTM files that complse the dem. In case you need more SRTM sections, download them and the combine into ne single srtm.tif file.
To download you can use:  https://dwtkns.com/srtm30m/
For this case the specific piece to download is N43E013
![srtm](https://user-images.githubusercontent.com/10267112/218804699-c395a8e8-d085-41a2-8340-e26355b1bfe5.JPG)



Then you have to identify the lake point and the down dam point.  
![inputPoints](https://user-images.githubusercontent.com/10267112/218804799-ba885bbf-09b8-4e9b-ab7a-d7f8d520805b.png)

The lake point is a point very close to the dam and where the level is constant in the SRTM file representing the surface of the upstream lake.

The down Dam point is a point downstream the dam. The difference in height of these two points represent the dam water jump.

time python creaFiles.py -d ./Cingoli -s /data/N43E013.hgt -lp  13.161652  43.382106 -w 0.1 -dp  13.163041  43.384161   -bbox "13.092161  43.343359 13.724455  43.731141"

The result is the following:
time python creaFiles.py -d ./Cingoli -s /data/N43E013.hgt -lp  13.161652  43.382106 -w 0.1 -dp  13.163041  43.384161   -bbox "13.092161  43.343359 13.724455  43.731141"
*************************************************
*   Preparation of file for NAMIDANCE DB calc
*************************************************
srtm file     = ./Cingoli//data/N43E013.hgt
Lake Point    = [13.161652, 43.382106]
Down dam Point= [13.163041, 43.384161]
output DEM    = ./Cingoli/outDem.grd
output Lake   = ./Cingoli/outLake.grd
resizing dem ./Cingoli//data/N43E013.hgt to   =   new file=./Cingoli/srtmNew.tif  to: 13.092161  43.343359 13.724455  43.731141
gdalwarp  -r near -te 13.092161  43.343359 13.724455  43.731141 ./Cingoli//data/N43E013.hgt ./Cingoli/srtmNew.tif
Creating output file that is 2276P x 1396L.
Processing ./Cingoli//data/N43E013.hgt [1/1] : 0Using internal nodata values (e.g. -32768) for image ./Cingoli//data/N43E013.hgt.
Copying nodata values from source ./Cingoli//data/N43E013.hgt to destination ./Cingoli/srtmNew.tif.
...10...20...30...40...50...60...70...80...90...100 - done.
Opening dem: ./Cingoli/srtmNew.tif
data type:  Int16
-19 793 -32768.0 0.0002778093145869947 2276 1396
reshaping file as 2276 1396
row col of lake 1257 250
Lake dem= 327    Downdam dem= 294    Jump= 33
2 True False
delta, dmax= 100 2026
delta, dmax= 200 2026
delta, dmax= 300 2026
delta, dmax= 400 2026
delta, dmax= 500 2026
delta, dmax= 600 2026
delta, dmax= 700 2026
delta, dmax= 800 2026
delta, dmax= 900 2026
delta, dmax= 1000 2026
delta, dmax= 1100 2026
delta, dmax= 1200 2026
delta, dmax= 1300 2026
delta, dmax= 1400 2026
delta, dmax= 1500 2026
delta, dmax= 1600 2026
delta, dmax= 1700 2026
delta, dmax= 1800 2026
delta, dmax= 1900 2026
delta, dmax= 2000 2026
vv# 1251 1255

real    0m11.197s
user    0m6.886s
sys     0m0.879s
