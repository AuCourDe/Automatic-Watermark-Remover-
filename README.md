# Automated Watermark Mask

Fully automated mask creation on text based watermarks. 

<p align="center">
    <img width="500" height="250" src="https://github.com/AuCourDe/watermark_mask/blob/master/sample.jpg" alt="sample oof picture to mask">
    <img width="500" height="250" src="https://github.com/AuCourDe/watermark_mask/blob/master/samplemask.png" alt="sample of mask">
</p>

# Instructions

1. [Download](https://github.com/AuCourDe/watermark_mask/archive/refs/heads/master.zip) the Github Repository

2. Download and install [Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/) if necessary. For this project recomended Python is 3.9 (maximum 3.11 due to tenssorflow compatibile)

3. Install libraries with `pip3 install -r requirements.txt` or `python3 -m pip install -r requirements.txt` .

4. Run `python3 main.py` in your code editor. Try this project on sample file or set path to your image (instead of sample.jpg).

5. Your mask for watermark remove is ready to use. This mask can be procesed to remove watermark fully automated  by generative AI model (run in Stable Diffusion). To fast remove watermark I recomend lama-cleaner aka IOPaint (https://github.com/Sanster/IOPaint)

6. Lama-Cleaner/IOpaint instalation
`pip3 install iopaint`

7. Run Lama-Cleaner / IOpaint
`iopaint run --model=lama --device=cpu \
--image=/path/to/image_folder \
--mask=/path/to/mask_folder \
--output=output_dir`

 or
`iopaint start --model=lama --device=cpu --port=8080`

Changes log:

V2
- Input path to folder of pictures
- Input path to folder including folders of pictures
- Full screen screenshots are now accepted. Part of screenshot containing picture now is croped to picture size only.
- QR code detection (partly visible QR codes usually not detected)
- Automatic run IOpaint after mask of folder. If many folders than many IOpaint can run simultaneously - performance decrease. 
- Watermark detection work on GPU, IOPaint running on CPU to not fight for resources.
- Estimated time, log

todo:
all coments in english
optimization
verification if IOpaint has finished first job then run with next folder instead of run many IOpain simultaneously.


V1
Create mask for picture
