# Welcome to Dilan's folder

Here, I am currently working on the OpenCV portion of the project

Hopefully, this personal log of occurences will prove useful down the line as we work on the final report and the weeklies. *(Also this is just an excuse to learn Markdown xdd)*  

## Week of 3-17-2023

### Tasks completed
*Successfully got the camera calibrated*  

This was pretty challenging, since I had to get into the weeds of  
how the OpenCV library worked. Regardless, I went ahead and added  
comments on what certain functions returned, what were their params,  
etc. This is with the hope that, as the project advances, everyone  
is on the same page and understands how the technology works.  


### Tasks to be completed
*Calculate distance between tags IRL*  

Now that the camera is properly calibrated, we can move on to the  
question of distance calculation. Some potential challenges may  
be the camera itself, which is ~~dog shit~~ of lesser quality.  
Currently, the camera does not detect tags farther than about a  
yard, which may limit the size in which we can run the game, in  
turn making for a very boring demo. To remedy this, there are some  
articles on how to increase the range of the detection by using CV  
*M A G I C*. More likely, we'll just do the top-down view plan, as  
we can just use a calibrated webcam. It might even make the distance  
calculations more straightforward.

> -DCF  

---

## Week of 3-10-2023

### Tasks completed
*Successfully rectified a still image taken by the camera*  

The `straighten_image_fisheye.py` code now works and rectified a  
still image that was passed to it. Before that, there was a lot of  
data collection that had to be done. This was done with `snap.py`,  
a short program that can take pictures and write them to a specific  
folder. At first, the pictures taken were not the best for the  
calibration, since they were taken at more or less the same angle  
and in the same position without consistent variance. To remedy this,  
`snap.py` was given a grid in the GUI in order to take consistent  
sample photos for the training. The resulting photos did not include  
the grid itself, since I had two cam streams open, one for the sample  
to be collected and one for the user's convenience.  
  
```
while True:
    ret0, frame0 = cam.read()
    draw_grid(frame0, (3, 3))
    ret1, frame1 = cam.read()
```

### Tasks to be completed
*Finish calibration of the camera*  