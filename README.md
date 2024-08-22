# Watermark mask and remover
Automatic creation of watermark masks. Automatic removal of watermarks.

<p align="center">
<img width="500" height="250" src="https://github.com/AuCourDe/watermark_mask/blob/master/processed.jpg" alt="procesed file"></p>

# Functions
- Loads a file that contains watermarks. Creates a mask for the watermarks. Removes the watermarks using generative AI (external application IO Paint -> [Download](https://github.com/Sanster/IOPaint) or [pip] (https://github.com/Sanster/IOPaint)).
- Handles files that are screenshots of entire screens, where the image to be cleaned of watermarks is located. The application attempts to identify the location of the actual image and crops it to its correct size.
- Performs actions on all subfolders after specifying the path to a folder.
- For improved performance, watermark detection is performed using the GPU, and watermark removal is done on the CPU. If no dedicated GPU, everything is done on the CPU.


# Instalation

1. [Download](https://github.com/AuCourDe/watermark_mask/archive/refs/heads/master.zip) the Github Repository
2. Download and install Python 3 and pip if necessary. The recommended Python version for this project is 3.9 (up to a maximum of 3.11 due to TensorFlow compatibility).
3. Install the required libraries with pip install [pip] -r requirements.txt or [pip] python -m pip install -r requirements.txt.
4. Install Tesseract [Download] (https://github.com/UB-Mannheim/tesseract/wiki) and set enviroment path.
5. Install IO Paint [pip] (# Instalation)


# Usage
Run [pip] python main.py in your code editor. Set path to your folder with pictures or subfolders


Changes log:

V2
-Input path to the folder containing pictures.
-Input path to a folder that includes subfolders with pictures.
-Full-screen screenshots are now accepted. The part of the screenshot containing the picture is cropped to the picture’s size only.
-QR code detection (partially visible QR codes are usually not detected).
-IOpaint runs automatically after processing the mask of a folder. If there are many folders, multiple instances of IOpaint may run simultaneously, which can decrease performance.
-Watermark detection is performed on the GPU, while IOpaint runs on the CPU to avoid resource conflicts.
-Estimated time and logs are provided.

To Do:
-Translate all comments to English.
-Optimize (cache removal, chunk removal).
-Verify if IOpaint has completed its first job before running the next folder, instead of running multiple instances of IOpaint simultaneously.

V1
- Create a mask for a picture.
