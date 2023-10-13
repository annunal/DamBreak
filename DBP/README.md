# The Dam Break Platform description
## Introduction
The <b>Dam Break PLatform (DBP)</b> is a web application that streamlines and facilitates the estimation of the consequences of Dam Break events. It relies on several scripts that were published in this gitHub site, wrapped around a web tool that facilitates the preparation and running of a new event.

## Methodology
The dam break event preparation includes a number of actions to be performed, summarized here:
- definition of the domain area
- creation of the bathymetry area and identification of the lake
- definition of the break size,  gauges points and other relevant parameters, such as the problem time
- running the case
- analysis

### Selection of the dam to analyse
By clicking on Dams tab you can identify the country in which the dam is located
![image](https://github.com/annunal/DamBreak/assets/10267112/de31a724-a58b-4529-9ff8-5b943ca88d82)

Let's assume Italy.  The identify the dam for which you want to perform the analysis, let's suppose Santa Rosalia in Sicily  by clicking the specific dam icon
![image](https://github.com/annunal/DamBreak/assets/10267112/88c9d26e-f347-4585-a589-7b6fb9a004cf)
A list of the charactristics of the dam is apresented, obtained from the GranD dam database (*** reference)

![image](https://github.com/annunal/DamBreak/assets/10267112/567515e0-b440-46ce-af3a-34a11c5ddb10)

by clicking the link "Set as new case" the data related to this dam are used to create a new dam break case.
Now you can define:
- the domain area
- the lake area
- the gauge points
- the other parameters (i.e. problem time, resolution etc)

### Domain area
The domain area contains the whole lake upstram the dam and the expected flow path downstream. To select the domain area you can either define the bounding box filling the fields in the form or use the map and move the Bottom left and Top right icons that define the domain area.  By default the domain is initialy set as +1 -1 degree in longitude and latitude but of course those limits are generally very exhagerated.
![image](https://github.com/annunal/DamBreak/assets/10267112/08b1fef9-ee85-4c20-bf49-6046f4a7ab82)
Using the mouse you should reduce the limits to a more reasonobale area,  as little as possible to contain the computational effort but large enough to cintain the flow disharge for the time tyou want to analyse.
Clicking and dragging the icon the new limits are prepared buyt you need to double click the icons (one at time) to fix the limits.
A suitable initial domain for this case could be something like this:
![image](https://github.com/annunal/DamBreak/assets/10267112/5cfbd0e1-ae8c-43b2-94b1-ec54072e502b)
but if you have already performed a case, you can show the related flow depth by selecting previous calculation results.
![image](https://github.com/annunal/DamBreak/assets/10267112/33a689f8-a32c-4966-b13e-1a46b252f800)
It is important to limit the domain area to the minimum, as explained.

### Lake area
Once the domain area is prepared you should identify the lake area because the system will compute the location of the lake. This can be done by using the polygon tool and clicking around the lake, to form the deliniation of the lake area. This should not take so much time because it is not necessary to be procise; you just need to outline the area that you consider part of the lake.
![image](https://github.com/annunal/DamBreak/assets/10267112/f9095aee-ebcd-45ca-985e-4950815f6d99)

Once you end the drawing, press **Save**  button to save what you have delineated.

### Down Dam Point and Lake point
Those are important points because they define where the down dam area starts and where the lake starts. The system will flatten the topography (thus eliminating the dam) for a width specified by the parameters of the calculation and will  represent the opening of the dam (i.e. the break). You can either specify these two points manually or use the icons on the map by dragging and moving. Once you end moving double click on the icon to set that position.

For this specificv case the  two points could be the ones indicated in the figure below. The red area is the area that will be flatten to create the break.  By default the width of the break is assumed the whole size of the break as present in the dtabase but you can modify the width by changing the value in the arameters.
![image](https://github.com/annunal/DamBreak/assets/10267112/6bbbfcea-4c43-4179-91be-3bb02ce83cf9)

### Gauges selection
It is not mandatory but if you want to have the timelines at specific locations, you can define your own gauges. 

This is done by clicking on the map; the point will appear on the right of the maop, the textbox on the right. Bt default the namingof the gauges is POINT_xxx but you can change it providing a more meaningful name. The selection of the gauge points is much easier if a previous case has been performed already because you can click on the areas affected. If you do not have any previous case, you can initialize the gauges at approximate points and in a second run make them more precise.
![image](https://github.com/annunal/DamBreak/assets/10267112/12ccebe5-a72f-451f-9b9b-b9a6e33b72da)

At the end of the points selection do not forget to **Save** to presenrve the selcted points

### Other quantities to fill in the parameters of the calculation
- **Description**:  this is a free text that can be used to specify the case
- **SRTM upload:** you can use the preloaded SRTM 30m topography or use your own file for the topography
- **Resolution (m):** the default resolution is 30 m but for particularly large domains, you can use a larger value. Or a smaller one if your computation can be contained. The expected computation time is shown when you save a case in the lavel on top of the save button
- **Width (m):** this represents the size of the break in m
- **Depth (m):** the depth is the how much of the original dam height is preserved after the break. By default this is 0, which means a complete opening of width indicated at the point above. If you specify 10 m, for example, it means that of the x m of the height of the dam 10 m are not broken. If this value is higher than the dam height, no break is performed.
- **Dam Water Elevation (m):**  The elevation of the water in the lake, by definition, is assumed what is found in the topography.  You can rise this level to compute a more sever case, to simulate, for example, an overspilling from the top of the dam
- **Friction coefficient:**  by definition this value is 0.015 but you can increase or reduce to perform sensitivity analyses
- **Features:** please do not edit this as it represents the json feature computed for the lake area
- **Problem time (min):** by default is 10h (600 min) but you can modify according to your needs









