# Welcome to Dilan's folder

Here, I am currently working on the OpenCV portion of the project

Hopefully, this personal log of occurences will prove useful down the line as we work on the final report and the weeklies. *(Also this is just an excuse to learn Markdown xdd)*  

You can try a number for $n$ to verify. With $n=4$, $$\sum_{i=0}^{\lg{n}-1}1=\sum_{i=0}^{1}1=1+1=2=\lg{4}$$Generally, $$\sum_{i=a}^{b}1=b-a+1$$

## Week of 3-31-2023

### **Tasks completed**
*Webcam is calibrated*  

### *3-28*
We've finalized how we're gonna use the AprilTags. We will be suspending a camera above the arena, using five tags to denote the four corners of the arena as well as the center point of the arena for th mice to go towards if it gets too close to the outer bounds of the arena. Because we're no longer using sound localization via time delay, we can simply use the camera's frame of reference instead of real world frame of reference, which will make life a whole lot simpler (a rare comodity in these times)  

Thus, the frame now displays the current coordinates for each AprilTag's center

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/misc_img/putText.png "Drawing center coordinates on frame")  

The next step would be to find the distance between two tags in the camera frame and hopefully draw lines between the four corners. From here, detecting nw tags on the mice would be the next step for boundary detection. Apart from this, I did some grunt work, getting tags from the AprilTag repo, enlargening them in order to not have to rip off the wallpaper from the lab's walls, and some documentation here and there. (Mostly because my memory is like a collander with three inch holes and I forget everything, or as Gen-Z says it, i forgor :skull: )  

### *3-27*  
Started work on the webcam calibration. We took some very rough measurements of the area covered by the webcam from one of those hanging electrical outlet thingies. It's roughly 6x8 ft.  
I took 80 pictures for the calibration of the webcam, however following the same steps as for the mouse's webcam yielded unusable results. Need to investigate further.   

Removing the errata does not seem to work... until you remove literally half of the data lol. See for yourself

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/cal_op/target2.png "Before")  

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/rectified_img/result2.png "After")  

The change is not as significant as with the smaller mouse camera, which is to be expected. The webcams' lens is not as convex as the smaller one. Regardless, this is still important, since the four corners will contain the four tags on the ground that will be used to calculate the distances between the mice.  

### **Tasks to be completed**
~~*3-27: Start distance calculations*~~  
*3-28: Real-life distance is no longer necessary, but we still need a reliable way to measure distance between tags in the camera frame*  

> -DCF

---

## Week of 3-24-2023

*Spring break, cya next week*  
![Alt text](https://media1.giphy.com/media/2uI9paIuAWgaqfyX0Q/giphy.gif?cid=ecf05e476c0a3skc8tlmfyjtl7r656h2j99cncm2r75u8b7s&rid=giphy.gif "he's just like me frfr")

## Week of 3-17-2023

### **Tasks completed**
*Successfully got the camera calibrated*  

This was pretty challenging, since I had to get into the weeds of how the OpenCV library worked. Regardless, I went ahead and added comments on what certain functions returned, what were their params, etc. This is with the hope that, as the project advances, everyone is on the same page and understands how the technology works. Here are some before and after pics.  



![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/cal_op/target1.png "Before calibration")
![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/rectified_img/result.png "After calibration")


Pretty substantial change huh? Like a Proactiv commercial. Anyways, the straightening now occurs on the camera live feed, which was done by cropping out the black edges on the frame. This led to a pretty clear (albiet now reduced) representation of what the camera was seeing. 

### **Tasks to be completed**
*Calculate distance between tags IRL*  

Now that the camera is properly calibrated, we can move on to the question of distance calculation. Some potential challenges may be the camera itself, which is ~~dog shit~~ of lesser quality. Currently, the camera does not detect tags farther than about a yard, which may limit the size in which we can run the game, in turn making for a very boring demo. To remedy this, there are some articles on how to increase the range of the detection by using CV *M A G I C*. More likely, we'll just do the top-down view plan, as we can just use a calibrated webcam. It might even make the distance calculations more straightforward.

> -DCF  

---

## Week of 3-10-2023

### **Tasks completed**
*Successfully rectified a still image taken by the camera*  

The `straighten_image_fisheye.py` code now works and rectified a still image that was passed to it. Before that, there was a lot of data collection that had to be done. This was done with `snap.py`, a short program that can take pictures and write them to a specific folder. At first, the pictures taken were not the best for the calibration, since they were taken at more or less the same angle and in the same position without consistent variance. To remedy this, `snap.py` was given a grid in the GUI in order to take consistent sample photos for the training. The resulting photos did not include the grid itself, since I had two cam streams open, one for the sample to be collected and one for the user's convenience.  
  
```
while True:
    ret0, frame0 = cam.read()
    draw_grid(frame0, (3, 3))
    ret1, frame1 = cam.read()
```

Additionally, some versatility has been added in order to ease the switch between the Jetson and my Windows machine when accessing certain directories.  

### **Tasks to be completed**
*Finish calibration of the camera*  

So far, the calibration is almost done. There are some black edges that need to be cropped out (easy) and there needs to be a reliable way to calibrate the live feed of the camera (not so easy). However, with the groundwork set this week, I'm confident that it won't be too bad to integrate. Surely, right?  

![url](https://cdn.frankerfacez.com/emoticon/652079/4)

> -DCF

---