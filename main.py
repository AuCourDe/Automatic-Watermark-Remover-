import os
from datetime import datetime
import keras_ocr
import cv2
import math
import numpy as np
from PIL import Image as image
import subprocess
import shutil
from pyzbar.pyzbar import decode
import time
from pathlib import Path

def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2) / 2)
    y_mid = int((y1 + y2) / 2)
    return (x_mid, y_mid)

def inpaint_text(img_path, pipeline):
    img = keras_ocr.tools.read(img_path)
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    avoided_box_counter = 0
    inpainted_img = mask  # Inicjalizacja jako obraz (mask)

    # create boxes of text
    for box in prediction_groups[0]:
        x0, y0 = box[1][0]
        x1, y1 = box[1][1]
        x2, y2 = box[1][2]
        x3, y3 = box[1][3]

        xx = x1 - x0
        yy = y2 - y1

        if yy <= xx:  # jeśli yy większy od xx, to oznacza, że wykryto tekst pionowy
            x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
            x_mid1, y_mid1 = midpoint(x0, y0, x3, y3)

            thickness = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)) + 15
            cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mid1), 255, thickness)

            inpainted_img = image.fromarray(mask)
        else:
            avoided_box_counter += 1

    return inpainted_img

def create_qr_mask(image_path):
    image = cv2.imread(image_path)

    # Dekodowanie kodów QR
    decoded_objects = decode(image)

    if decoded_objects:
        # Wyodrębnienie punktów kodu QR
        points = []
        for obj in decoded_objects:
            x, y, w, h = obj.rect
            points.append([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])

        # Interpolacja punktów QR
        points = qr_code_interpolation(points, 15)

        # Tworzenie maski
        mask = np.zeros_like(image, dtype=np.uint8)
        for point in points:
            cv2.fillConvexPoly(mask, np.array(point), (255, 255, 255))
    else:
        # Utworzenie pustej maski
        mask = np.zeros_like(image, dtype=np.uint8)

    return mask

def qr_code_interpolation(points, size_of_qr_border):
    new_points = []
    for point in points:
        x1, y1 = point[0]
        x2, y2 = point[1]
        x3, y3 = point[2]
        x4, y4 = point[3]

        # left top corner
        x1n = x1 - size_of_qr_border
        y1n = y1 - size_of_qr_border
        # right top
        x2n = x2 + size_of_qr_border
        y2n = y2 - size_of_qr_border
        # right bottom
        x3n = x3 + size_of_qr_border
        y3n = y3 + size_of_qr_border
        # left bottom
        x4n = x4 - size_of_qr_border
        y4n = y4 + size_of_qr_border

        new_points.append([[x1n, y1n], [x2n, y2n], [x3n, y3n], [x4n, y4n]])

    return new_points

def rotate_part_mask(file_path, angle, cache_patch, pipeline):
    # Wczytaj obraz
    img = image.open(file_path)

    # Obróć zdjęcie i zrób OCR
    rotated_img = img.rotate(angle, expand=True, resample=image.BICUBIC)
    rotated_img_path = Path(cache_patch) / f"rotated{angle}.png"
    rotated_img.save(rotated_img_path)

    rotated_mask = inpaint_text(str(rotated_img_path), pipeline)

    if isinstance(rotated_mask, np.ndarray):
        rotated_mask = image.fromarray(rotated_mask)

    # Obróć maskę o przeciwny kąt, aby przywrócić oryginalny kąt
    restored_mask = rotated_mask.rotate(-angle, expand=True, resample=image.BICUBIC)
    restored_mask_path = Path(cache_patch) / f"masked{angle}.png"
    restored_mask.save(restored_mask_path)

    # Oblicz różnicę w wymiarach po obróceniu
    delta_width = restored_mask.width - img.width
    delta_height = restored_mask.height - img.height

    # Przytnij przywrócone zdjęcie do oryginalnego rozmiaru
    restored_img = restored_mask.crop(
        (delta_width // 2, delta_height // 2, img.width + delta_width // 2, img.height + delta_height // 2))
    restored_img_path = Path(cache_patch) / f"masked{angle}_360.png"
    restored_img.save(restored_img_path)

    return str(restored_img_path)

def rotate_and_mask(file_path, mask_folder, cache_patch, pipeline):
    angle0_mask = rotate_part_mask(file_path, 0, cache_patch, pipeline)
    angle1_mask = rotate_part_mask(file_path, 45, cache_patch, pipeline)
    angle2_mask = rotate_part_mask(file_path, 90, cache_patch, pipeline)
    angle3_mask = rotate_part_mask(file_path, 270, cache_patch, pipeline)
    angle4_mask = rotate_part_mask(file_path, 315, cache_patch, pipeline)

    qr_mask_path = Path(cache_patch) / "qr_mask.png"
    qr_masked = create_qr_mask(file_path)
    cv2.imwrite(str(qr_mask_path), cv2.cvtColor(qr_masked, cv2.COLOR_BGR2RGB))

    mask0 = cv2.imread(str(angle0_mask)).astype("float32")
    mask1 = cv2.imread(str(angle1_mask)).astype("float32")
    mask2 = cv2.imread(str(angle2_mask)).astype("float32")
    mask3 = cv2.imread(str(angle3_mask)).astype("float32")
    mask4 = cv2.imread(str(angle4_mask)).astype("float32")
    mask5 = cv2.imread(str(qr_mask_path)).astype("float32")

    # add masks together to create one final mask
    result = 255 * (mask0 + mask1 + mask2 + mask3 + mask4 + mask5)
    result = result.clip(0, 255).astype("uint8")

    final_mask_path = Path(mask_folder) / os.path.basename(file_path)
    cv2.imwrite(str(final_mask_path), result)

def extract_photo(file_name, ratio):
    # Wczytaj obraz
    image = cv2.imread(file_name)
    height, width, _ = image.shape
    start_y = 0
    end_y = height - 1

    # Szukaj początku zdjęcia
    for y in range(height):
        row = image[y]
        unique_colors = np.unique(row, axis=0)
        unique_colors_ratio = len(unique_colors) / width
        if unique_colors_ratio >= ratio:
            start_y = y
            break

    # Szukaj końca zdjęcia
    for y in range(height - 1, -1, -1):
        row = image[y]
        unique_colors = np.unique(row, axis=0)
        unique_colors_ratio = len(unique_colors) / width
        if unique_colors_ratio >= ratio:
            end_y = y
            break

    # Wytnij zdjęcie
    extracted_image = image[start_y:end_y + 1, :]

    # Sprawdź, czy rozmiar zwróconego zdjęcia jest mniejszy lub równy 20% oryginalnego rozmiaru
    if (end_y - start_y + 1) / height <= 0.2:
        return image  # Zwróć oryginalne zdjęcie
    else:
        return extracted_image  # Zwróć wycięte zdjęcie


def rename_files(directory):
    # current date and time for renaming purpose
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S%f")
    for filename in os.listdir(directory):
        old_filepath = os.path.join(directory, filename)
        if os.path.isfile(old_filepath):
            # check sufix
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            # acceptable suffixes: .jpg and .png
            if ext in ['.jpg', '.png']:
                # create new filename
                new_filename = f"image_{current_datetime}{ext}"
                new_filepath = Path(directory) / new_filename
                # check if new file created
                index = 1
                while os.path.exists(new_filepath):
                    new_filename = f"image_{current_datetime}_{index}{ext}"
                    new_filepath = Path(directory) / new_filename
                    index += 1
                # change file name
                os.rename(old_filepath, new_filepath)
                print(f"File name changed: {filename} -> {new_filename}")

def copy_images(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(('.jpg', '.png')):
            source_file_path = Path(source_folder) / filename
            destination_file_path = Path(destination_folder) / filename
            shutil.copyfile(source_file_path, destination_file_path)

def estimate_remaining_time(start_time, current_progress, total_progress):
    """
    Estymuje pozostały czas na podstawie dotychczasowego postępu i czasu rozpoczęcia.

    Args:
    - start_time: Czas rozpoczęcia w sekundach.
    - current_progress: Aktualny postęp.
    - total_progress: Całkowity postęp do osiągnięcia.

    Returns:
    - Pozostały czas w sekundach.
    """
    current_time = time.time()
    elapsed_time = current_time - start_time
    if current_progress == 0:
        return None  # Nie można oszacować, gdy postęp wynosi 0
    else:
        avg_progress_per_second = current_progress / elapsed_time
        remaining_progress = total_progress - current_progress
        remaining_time_seconds = remaining_progress / avg_progress_per_second

        remaining_hours = int(remaining_time_seconds / 3600)
        remaining_minutes = int((remaining_time_seconds % 3600) / 60)
        remaining_seconds = int(remaining_time_seconds % 60)

        return remaining_hours, remaining_minutes, remaining_seconds

if __name__ == "__main__":
    # zapisywanie jako jpg zamiast png
    # rozwiązanie częsci probemu z polskimi znakami https://stackoverflow.com/questions/44330084/opencv-imwrite-doesnt-work-because-of-special-character-in-file-path
    full_folder_path = input("Enter the folder path: ")
    os.chdir(full_folder_path)
    list_of_folders = os.listdir(full_folder_path)
    pipeline = keras_ocr.pipeline.Pipeline()
    for folder in list_of_folders:
        folder_path = os.path.join(full_folder_path, folder)
        if os.path.isdir(folder_path):
            print(f"Current folder is {folder_path}")
            start_time = time.time()
            file_name_counter = 0
            cache_path = Path(folder_path) / 'cache'
            cache_path.mkdir(exist_ok=True)
            croped_folder = Path(folder_path) / 'croped'
            croped_folder.mkdir(exist_ok=True)
            cleaned_folder = Path(folder_path) / 'cleaned'
            cleaned_folder.mkdir(exist_ok=True)
            mask_folder = Path(folder_path) / 'mask'
            mask_folder.mkdir(exist_ok=True)

            copy_images(folder_path, cache_path)
            rename_files(cache_path)

            for file_name in os.listdir(cache_path):
                file_path = cache_path / file_name
                if file_path.is_file() and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    extracted_photo = extract_photo(str(file_path), 0.3)
                    output_path = croped_folder / file_name
                    cv2.imwrite(str(output_path), extracted_photo)
                    print(f"Picture extracted to: {output_path}")

            total_file_names = len(os.listdir(croped_folder))
            for file_name in os.listdir(croped_folder):
                file_path = croped_folder / file_name
                if file_path.is_file() and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_name_counter += 1
                    print(f"Working on file {file_name_counter} from {total_file_names}. Current file name is {file_path}")
                    rotate_and_mask(str(file_path), str(mask_folder), str(cache_path), pipeline)

                    current_progress = file_name_counter
                    remaining_time = estimate_remaining_time(start_time, current_progress, total_file_names)
                    if remaining_time is not None:
                        hours, minutes, seconds = remaining_time
                        print(f"Remaining time: {hours} hours {minutes} minutes {seconds} seconds. Inpainting proces not included, about 140 picture per hour on RTX3060")
                    else:
                        print("Cannot estimate remaining time when progress is 0.")

            try:
                os.rmdir(cache_path)
            except:
                print(f"Something wrong during cache remove.")

            program_path = "iopaint"
            program_arguments = ["run", "--model=lama", "--device=cpu", f"--image={croped_folder}", f"--mask={mask_folder}", f"--output={cleaned_folder}"] #"--device=cuda"
            subprocess.run(["start", "cmd", "/c", program_path] + program_arguments, shell=True)
#             wait fof one terminal working / jeden pracujący, jeżeli drugi to czekaj.
