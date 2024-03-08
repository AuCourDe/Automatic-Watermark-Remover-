import matplotlib.pyplot as plt
import keras_ocr
import cv2
import math
import numpy as np
import tensorflow #remember to add system path to tesserac
from PIL import Image as image
from math import ceil

# based on inpaint idea on https://towardsdatascience.com/remove-text-from-images-using-cv2-and-keras-ocr-24e7612ae4f4
# - todo
# - open many files
# - save many mask files
# - with open and save chunks
# - angles move to def like argument
# - v2 find watermark by segmentation - opencv + sample of watermark + training allow to find all watermarks not only by ocr


# calculating midpoint for boxes
def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)

# calcualting boxes, ocr, inpainting
def inpaint_text(img_path, pipeline, remove_list):
    img = keras_ocr.tools.read(img_path) 
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    avoided_box_counter = 0
#    create boxes of text
    for box in prediction_groups[0]:
        # uncoment to manualy check boxes of text
        # print(f"box{box}")
        x0, y0 = box[1][0]
        x1, y1 = box[1][1] 
        x2, y2 = box[1][2]
        x3, y3 = box[1][3] 

        #check if box shape is longer than higher. If highier than longer than mean vrong interpretation by ocr.
        xx = x1 - x0
        yy = y2 - y1
        # uncoment to manualy check vertical text wrong interpetation status
        # print(xx)
        # print(yy)

        if yy <= xx: #if yy higher than xx that mean vertical text recognized
            # create midpoint to reduce coordinates
            x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
            x_mid1, y_mid1 = midpoint(x0, y0, x3, y3)

            #create mask and inpaint each boxes
            thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )) 
            inpainted_img = cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mid1), 255, thickness)
        else:
            avoided_box_counter += 1
            print(f" {avoided_box_counter} - box avoided due to wrong ocr interpretation of vertical text")
         
    return(inpainted_img)

img_path_absolute = "sample.jpg"
chunk45 = "45chunk.png"
write45 = "45write.png"
chunk315 = "315chunk.png"
write315 = "315write.png"
final_mask = "samplemask.png"

# ocr
pipeline = keras_ocr.pipeline.Pipeline()

# list of word to remove, null = all
remove_list = []

#change angle from 0 to 45 esecial for sample image
img = image.open(img_path_absolute)
rotated45 = img.rotate(45)
rotated45 = rotated45.save(chunk45)
img_path = chunk45
# mask at angle 45
masked45 = inpaint_text(img_path, pipeline, remove_list)
cv2.imwrite(write45, cv2.cvtColor(masked45, cv2.COLOR_BGR2RGB))
img = image.open(write45)
# rortate to angle 0
rotated45 = img.rotate(315)
rotated45 = rotated45.save(chunk45)


# change angle from 45 to 315 esecial for sample image
img = image.open(img_path_absolute)
rotated315 = img.rotate(315)
rotated315 = rotated315.save(chunk315)
img_path = chunk315
masked315 = inpaint_text(img_path, pipeline, remove_list)
cv2.imwrite(write315, cv2.cvtColor(masked315, cv2.COLOR_BGR2RGB))
img = image.open(write315)
rotated315 = img.rotate(45)
rotated315 = rotated315.save(chunk315) 

# read created mask
mask1 = cv2.imread(chunk45).astype("float32")
mask2 = cv2.imread(chunk315).astype("float32")

# add masks togheter to create one final mask
result = 255*(mask1 + mask2)
result = result.clip(0, 255).astype("uint8")

# uncoment to show results direct in python
# cv2.imshow('result', result)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# save results
cv2.imwrite(final_mask, result)