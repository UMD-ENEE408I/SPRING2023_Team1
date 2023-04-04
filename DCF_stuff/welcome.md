# Welcome to Dilan's folder

Here, I am currently working on the OpenCV portion of the project

Hopefully, this personal log of occurences will prove useful down the line as we work on the final report and the weeklies. *(Also this is just an excuse to learn Markdown xdd)*  


## Week of 4-7-2023

### **Tasks completed**  
*Started work on the arena drawing*  

### *4-4*  
I've implemented the code in order to draw the arena on the frame. As of writing, it seems to work for a split second before commiting sudoku. 

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/9aa48930798eaac55f0648723f83e0de2751e048/DCF_stuff/opencv/misc_img/draw_arena.png "Drawing arena")

```python
for res in results:
    for x in range(len(results)):
        if x not in detect_arr:
            detect_arr.add(results[x].tag_id)
        
        print(detect_arr)
        if corner_tags.intersection(detect_arr) == corner_tags:
            cv2.line(ud_img, (int(results[0].center[0]), int(results[0].center[1])), (int(results[1].center[0]), int(results[1].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(results[1].center[0]), int(results[1].center[1])), (int(results[2].center[0]), int(results[2].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(results[2].center[0]), int(results[2].center[1])), (int(results[3].center[0]), int(results[3].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(results[3].center[0]), int(results[3].center[1])), (int(results[0].center[0]), int(results[0].center[1])), color=(0, 255, 0), thickness=5)
```
This is the code that's causing me to age faster. The problem is that `results` is dynamic, and therefore changes depending on how many detections there are. I'm pretty sure I need to adjust the way detections are added and removed to `detect_arr`, that it, to actually remove tags that are no longer in frame / detected.  

*Update*  
It's finished! With a nudge from Levi, I managed to implement the tag storage as a ~~hash~~ dictionary (sorry, the Ruby programmer in me made an unexpected apperance). Regardless, here's how I managed it

```python
corner_tags = [0,1,2,3]
while True:
...
    try:
        detect_arr = dict()
    ...
    for res in results:
        # For however many detections there are, we add the detection 
        # into the 'detect_arr' dictionary if it is one of the pre-determined
        # tag numbers for the corners.  
        for x in range(len(results)):
            if x in corner_tags:
                detect_arr.update({results[x].tag_id: results[x]})
        # Turn the keys of the dictionary into a list so we can sort the dictionary
        detect_keys = list(detect_arr.keys())
        detect_keys.sort()
        # Using a codeblock (PogChamp), we can iterate through the array and change 
        # the indices so that the dedections are ordered by the tags. 
        sorted_dict = {i: detect_arr[i] for i in detect_keys}
        print(detect_keys)

        # Since we have sorted our dictionary, we can go ahead and draw the rectangle 
        # confident that the indicies shown below will be accurate. 
        if set(detect_keys) & set(corner_tags) == set(corner_tags):
            cv2.line(ud_img, (int(sorted_dict[0].center[0]), int(sorted_dict[0].center[1])), (int(sorted_dict[1].center[0]), int(sorted_dict[1].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(sorted_dict[1].center[0]), int(sorted_dict[1].center[1])), (int(sorted_dict[2].center[0]), int(sorted_dict[2].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(sorted_dict[2].center[0]), int(sorted_dict[2].center[1])), (int(sorted_dict[3].center[0]), int(sorted_dict[3].center[1])), color=(0, 255, 0), thickness=5)
            cv2.line(ud_img, (int(sorted_dict[3].center[0]), int(sorted_dict[3].center[1])), (int(sorted_dict[0].center[0]), int(sorted_dict[0].center[1])), color=(0, 255, 0), thickness=5)
```
As of right ***now***, this will only work with the tags that are in `corner_tags`. Anyt 

### *4-3*  
So far, we've gotten the webcam calibrated and undistorted (see week 3-31). Today, we start work on the printing of the detections, consequently drawing the box of the arena on the screen. Last week, we managed to print out the coordinates of the tags. Today, we want to use these detections and distinguish between the different tags detected. This is proving difficult because ~~I am a dumbass and~~ the documntation is ~~ass~~ fussy. So far, this is my approach to tag distinction:  

```python
for res in results:
    for x in range(len(results)):
        if x not in detect_arr:
            detect_arr.append(results[x].tag_id)
        print(detect_arr)
```  
It bugs me because this isn't the most elegant way to do this, and it's also still not working as intended. When I detect two tags, its works fine-ish, but since I'm currently using my laptop screen to display the tags, sometimes the camera picks up the smaller tags that show up in the cv frame, and it freaks out and starts appending more and more to `detect_arr`.  

```python
[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
```  
ASOASF you get the idea.  

I think it has something to do with the funky way `Detections` are stored / organized. I had hardcoded some limitations on the number of elements that would trigger the code snippet, but 216 taught me that hard-coding is a cardinal sin, so I wanted something more flexible.  

Literally 5 min after writing this I fixed it lol. I changed `detect_arr` to a set, that way duplicates are not allowed.  
```python
detect_arr = set()

...

for res in results:
    for x in range(len(results)):
        if x not in detect_arr:
            detect_arr.add(results[x].tag_id)
        print(detect_arr)
```

Now, sets are a bit fussier than arrays, so this may come back to bite me in the ass. [But I'll just stick my head in the ground until it becomes too big to ignore.](https://en.wikipedia.org/wiki/Ostrich_algorithm) For now, it seems to work fine, even with more than 2 tags.  

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/f8ce17c2d615e337fe25fe60c6739bb798fb000d/DCF_stuff/opencv/misc_img/detect_tags.png "Multiple tags detected")  


The real test will be tomorrow, where I plan to print out some tags on paper and try drawing lines between them. However, since the mice will also have tags on them, we need to make sure that only the tags that we have set to be corners (AKA 0 - 3) are the only ones that get lines drawn between them.  I was thinking something along the lines of: 

```
corners = Array of tag numbers 0 - 3
for res in results loop:
    If "corners" intersects with "detect_arr":
        line(center of 0 -> center of 1)
        line(center of 1 -> center of 2)
        line(center of 2 -> center of 3)
        line(center of 3 -> center of 1)
```  
As is, this looks pretty messy, so I think I may just make this a function to make it a bit cleaner. 


### **Tasks to be completed**  
*4-3 Finish drawing the arena's box in the frame*

>DCF

---  

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

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/37e64de9fca4522aa44ac6d9588f4d121fe72618/DCF_stuff/opencv/cal_op/target2.png "Before")  

![Alt text](https://github.com/UMD-ENEE408I/SPRING2023_Team1/blob/bc752b24b6080a9bb441f6104593d13025a1d84b/DCF_stuff/opencv/rectified_img/result2.png "After")  

The change is not as significant as with the smaller mouse camera, which is to be expected. The webcams' lens is not as convex as the smaller one. Regardless, this is still important, since the four corners will contain the four tags on the ground that will be used to calculate the distances between the mice.  

### **Tasks to be completed**
~~*3-27: Start distance calculations*~~  
*3-28: Real-life distance is no longer necessary, but we still need a reliable way to measure distance between tags in the camera frame*  

> -DCF

---

## Week of 3-24-2023

*Spring break, cya next week*  
![Alt text](https://media1.giphy.com/media/2uI9paIuAWgaqfyX0Q/giphy.gif?cid=ecf05e476c0a3skc8tlmfyjtl7r656h2j99cncm2r75u8b7s&rid=giphy.gif "vibin'")

>DCF

---

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
  
```python
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