# Async Profile Image

This repository contains code for displaying a profile image. If you want to display a rectangular image, then use ProfileImage. If you want to use a circular image, then use a CircularProfileImage. In both cases, you will want to set the source of the profile image and then call update_crop_values with the width, height, center_x, and center_y values that you want applied to the image. These can be calculated manually, say from a database, or given from the ProfileImageCropper widget.

# Profile Image Cropper
The cropping widget itself might have bugs related to its positioning, but using the regular cropper which will impose a square, or the circular cropper which will impose a circle will allow for the generation of custom cw, ch, cx, cy coordinates for use in a profile image. These can be retrieved using the get_image_crop command, and an example can be found in the sample.kv file.