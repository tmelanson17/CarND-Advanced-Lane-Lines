## Writeup Template

### You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./calib/undistort.png "Undistorted"
[image2]: ./transform/undistort.png "Road Transformed"
[image3]: ./thresholded_images/result_5.png "Binary Example"
[image4]: ./transform/warped.png "Warp Example"
[image5]: ./polyfit/color_lane_lines.png "Fit Visual"
[image6]: ./polyfit/lane_proj.png "Output"
[image7]: ./calib/input.png "Input"
[image8]: ./calib/points.png "Finding Chessboard Points"
[video1]: ./project_video.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in the cells in `calibration.ipynb`

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

![alt text][image7]
![alt text][image8]

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][image1]

### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:
![alt text][image2]

I saved the parameters from the calibration into a file called `camera_values.p`. After loading the values using pickle, I used `cv2.undistort()` on the image to obtain the original values.

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

I used a combination of color and gradient thresholds to generate a binary image (thresholding steps at lines 4 through 30 in `threshold.py`).  Here's an example of my output for this step. First, I used a Sobel horizontal filter, as well as a saturation filter, to obtain the images. Because I found that shadows tend to have high saturation values, I also set a minimum luminance for the lane line to register.

![alt text][image3]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes a function called `corners_unwarp()`, which appears in lines 6 through 20 in the file `transform.py` (output_images/examples/example.py) (or, for example, in the 3rd code cell of the IPython notebook).  The `corners_unwarp()` function takes as inputs an image (`img_undistort`), as well as source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner:

```python
src_pts = np.float32([[581, 460],
                      [206, 720], 
                      [1107, 720], 
                      [702, 460]])

dst = np.float32(
    [[(img_size[0] / 4), 0],
    [(img_size[0] / 4), img_size[1]],
    [(img_size[0] * 3 / 4), img_size[1]],
    [(img_size[0] * 3 / 4), 0]])
```

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 581, 460      | 320, 0        | 
| 206, 720      | 320, 720      |
| 1107, 720     | 960, 720      |
| 702, 460      | 960, 0        |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image4]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

To detect the lanes, I followed the Udacity project's lead of creating a histogram of possible lane points in the bottom half of the image along the horizontal axis. The index of the peak magnitude on the left side and on the right side of the image were recorded and used as the initial left and right hand sides. 

To fit the curve, I divided the lane line into n=20 sections and did the following for each horizontal section:
1. Find the nonzero sections of the curve
2. Determine which points were within {window=150}/2 of the left lane center and of the right lane center
3. Concatenated the list of points to the running total
4. Updated the left and right lane centers to the average of the recorded line lanes

![alt text][image5]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

For the curvature of the radius, I used the formula given in Udacity (based on calculating the change in theta over the change in arc length) to find the radius of curvature. I found the lane lines to be 700 pixels apart, and the lane line to be about 50 to 70 pixels at the base.


To find the lane center, I used the polynomial fit to find the lane bases at the bottom pixel (719), then took the average of the two. I assumed the vehicle center was the bottom-center pixel of the image. Then, I subtracted the lane center to the vehicle center, then used the earlier pixels to meter conversion for x to find the offset in meters.

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in `video-pipeline.ipynb` in the function `draw()` (it has its own section) as well as in the `draw.ipynb` file.  Here is an example of my result on a test image:

![alt text][image6]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./result.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

For one, I saw that while the lane lines fit reasonably well on the image, it would occasionally output a result that was way off. Initially, i just tried an average filter. However, the average filter only spread the outliar across multiple frames. As a solution, I decided to have a 'detect' function in the Lane class, which only would be True if the overall noise was drastically different from that of the previous frames. This got rid of the outliars, although the lane  marker is now less adaptable to bumps on the road.

Additionally, trying to distinguish the lane line from the guardrail was an issue. I initially tried to put a cap on the horizontal measurement (to prevent the shadows from having too much an influence). Using luminance may also be an option, as the strong gradients are caused by the shadow cast by the guardrail.

On the other hand, a median filter would be extremely helpful in a rather straight but not well-marked road. Because it takes an average, the noise caused by the extra points could be balanced out overall.
