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



