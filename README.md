# Automated Watermark Mask

Code to run a fully automated mask on text watermark.

# Instructions

1. [Download] the Github Repository

2. Download and install [Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/) if necessary. For this project recomended Python is 3.9 (maximum 3.11 due to tenssorflow compatibile)

3. Install libraries with `pip3 install -r requirements.txt` or `python3 -m pip install -r requirements.txt` .

4. Run `python3 main.py` in your code editor. Try this prject on sample file then set path to your image (instead of sample.jpg).

5. You have ready to use mask for watermark. This mask can be procesed fully automaeted to remove watermark be AI model (including Stable Diffusion) for example lama-cleaner aka IOPaint (https://github.com/Sanster/IOPaint)
`pip3 install iopaint`
`iopaint start --model=lama --device=cpu --port=8080`
 or

`iopaint run --model=lama --device=cpu \
--image=/path/to/image_folder \
--mask=/path/to/mask_folder \
--output=output_dir`
