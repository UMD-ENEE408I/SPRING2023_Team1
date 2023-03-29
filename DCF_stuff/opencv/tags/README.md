# Resizing Tags

### *Source of tags: https://github.com/AprilRobotics/apriltag-imgs under "tag36h11"*

Default size of the tags is too small to be used. Use the following instructions to resize  

```
convert <small_marker>.png -scale <scale_chosen_in_percent>% <big_marker>.png
```

This will create a new PNG in the same folder as the small one. You may need to install ImageMagick for this to work, which can be done with the following commands:  

```
sudo apt update
```

```
sudo apt install imagemagick
```

Once you've resized, you may check the new PNG in the folder via file explorer or:  

```
display <new>.png 
```

I've found that 5000% works to get the default tags to a respectable size, though you may want to resize them to different sizes to better suit your needs  

**NOTE**: This only works on Linux, and I can't be bothered to look up Windows instructions. Not like I'm being paid to write these instructions
