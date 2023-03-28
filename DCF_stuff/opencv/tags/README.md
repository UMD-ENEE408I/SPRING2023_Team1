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

**NOTE**: This only works on Linux, and I can't be bothered to look up Windows instructions. Not like I'm being paid to write these instructions xdd