# Dambreak sowftare tools
## Installation
Install conda, then create an environment  called gdal
conda create -n gdal
conda install gdal

A number of tools are available:
* <a href="https://github.com/annunal/DamBreak/blob/main/README.md#namidance-files-creation">Namidance files creation</a>
* [Arrival Time computation] (#arrival-time-computation)
* [Extraction of timelines] (#extraction-of-timelines)

## NAMIDANCE Files creation
To run use this command:
creaFiles.py [-d basedir] [-s srtm.tif] -w  0.3 -lp 36.32  36.19 -dp 36.12 37.42 [-od outDem.grd]  [-ol outLake.grd ]  [-bbox xmin ymin xmax ymax] [-res NewCellSize]

where:

* **-d** <dir>:  is the base directory. If is not specified the current directory is used
* **-s** <fname>:  is the SRTM file that is used [default:  srtm.tif].  You can specify more files included in double apices and separated by a + sign. In that case it will merge the files before cropping to the desired extent with bbox
* **-w** <sizeKM>:
* **-lp** <lon lat>:
* **-dp** <lon lat> 
* **-od** <output dem grid>
* **-ol** <output Lake grid>:
* **-bbox** <xmin ymin xmax ymax>
* **-res** <NewCellSize> in degrees


##Example: El Cajun (Honduras) dam break
![wholeArea](https://user-images.githubusercontent.com/10267112/218968706-29ab1a9e-53be-4596-b036-70241c9039de.png)


Identify the dedicated SRTM files that complse the dem. In case you need more SRTM sections, download them and the combine into ne single srtm.tif file.
To download you can use:  https://dwtkns.com/srtm30m/
For this case the specific piece to download is N43E013
![selection_srtm](https://user-images.githubusercontent.com/10267112/218966318-7aab2e1d-c40d-460a-a218-9949566eaf04.JPG)

Then you have to identify the lake point and the down dam point.  The lake point is a point very close to the dam and where the level is constant in the SRTM file representing the surface of the upstream lake.
![inputPoints](https://user-images.githubusercontent.com/10267112/218968378-faee4bea-8703-4eb3-9478-5c351106dbd2.png)


The down Dam point is a point downstream the dam. The difference in height of these two points represent the dam water jump.

  <pre>
time python creaFiles.py -d El_Cajun -s  "/data/N14W088.hgt+/data/N15W088.hgt"  -w 0.06  -lp -87.744886  15.02809  -dp -87.745366  15.030250 -bbox "-88. 14.800 -87.400 15.400"
  </pre>

The result is the following:
<pre>
*************************************************
*   Preparation of file for NAMIDANCE DB calc
*************************************************
srtm file     = /data/N14W088.hgt+/data/N15W088.hgt
Lake Point    = [-87.744886, 15.02809]
Down dam Point= [-87.745366, 15.03025]
output DEM    = El_Cajun/outDem.grd
output Lake   = El_Cajun/outLake.grd
gdal_merge.py  -o El_Cajun/srtmMerge.tif El_Cajun/data/N14W088.hgt El_Cajun/data/N15W088.hgt
0...10...20...30...40...50...60...70...80...90...100 - done.
resizing dem El_Cajun/srtmMerge.tif to   =   new file=El_Cajun/srtmNew.tif  to: -88. 14.800 -87.400 15.400
gdalwarp  -r near -te -88. 14.800 -87.400 15.400 El_Cajun/srtmMerge.tif El_Cajun/srtmNew.tif
Creating output file that is 2160P x 2160L.
Processing El_Cajun/srtmMerge.tif [1/1] : 0...10...20...30...40...50...60...70...80...90...100 - done.
Opening dem: El_Cajun/srtmNew.tif
data type:  Int16
17 2312 None 0.0002777777777777751 2160 2160
reshaping file as 2160 2160
row col of lake 1339 918
Lake dem= 285    Downdam dem= 266    Jump= 19
2 True False
delta, dmax= 100 1339
delta, dmax= 200 1339
delta, dmax= 300 1339
delta, dmax= 400 1339
delta, dmax= 500 1339
delta, dmax= 600 1339
delta, dmax= 700 1339
delta, dmax= 800 1339
delta, dmax= 900 1339
delta, dmax= 1000 1339
delta, dmax= 1100 1339
delta, dmax= 1200 1339
delta, dmax= 1300 1339
vv# 1334 1336

real    0m16.363s
user    0m7.101s
sys     0m2.013s
</pre>

  Now you can setup the Namidance calculation by secifying **outDem.grd** as bathymetry and **outLake.grd** as deformation file. Then the NAMIDANCE computation can start
 
  ![namidance_start](https://user-images.githubusercontent.com/10267112/218967068-f8d84762-3dc2-4c6b-bada-970b15817ff8.JPG)

