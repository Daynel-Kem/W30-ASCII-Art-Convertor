from PIL import Image
from image_slicer import slice_image
import sys
import cv2
import numpy as np
import os
import shutil

def img_to_ascii(image_path, height, width):
    # Input image and parameters
    img = Image.open(image_path)

    os.mkdir("middle")
    os.mkdir("middle2")

    # Grayscale it
    gray_img = img.convert('L')
    gray_img.save("middle/gray.jpg")

    # Split the image into n x m pixels based on the inputted file (auto do it if not provided)
    slice_image(
        source="middle/gray.jpg",
        output_dir="middle2",
        tile_height=height,
        tile_width=width,
        naming_format="{row}-{col}.jpg"
    )

    # Assign each pixel a darkness number value
    pixels = []
    def measure_darkness_opencv(img_path):
        if img_path == '\n':
            return '\n'
        im = cv2.imread(img_path)
        return np.mean(im)
    
    order = []

    middle2_path = "middle2"
    with os.scandir(middle2_path) as tiles:
        for tile in tiles:
            order.append(tile.path)

    def sort_dash_separated(strings):
        """
        Sort a list of strings in format "path/{int}-{int}.ext" where the first int
        takes precedence, then the second int.
        """
        def get_sort_key(s):
            # Get just the filename without the directory path
            filename = s.split('/')[-1]
            # Remove file extension
            name_without_ext = filename.rsplit('.', 1)[0]
            # Split on dash and convert to ints
            return tuple(map(int, name_without_ext.split('-')))
        
        return sorted(strings, key=get_sort_key)
    
    def add_newlines_on_first_int_change(strings):
        """
        Add '\\n' to the array wherever the first {int} in the format changes.
        
        Example:
            >>> add_newlines_on_first_int_change(['middle2/0-1.jpg', 'middle2/0-2.jpg', 'middle2/1-0.jpg'])
            ['middle2/0-1.jpg', 'middle2/0-2.jpg', '\\n', 'middle2/1-0.jpg']
        """
        if not strings:
            return strings
        
        result = []
        prev_first_int = None
        
        for s in strings:
            # Extract filename from path
            filename = s.split('/')[-1]
            # Remove extension
            name_without_ext = filename.rsplit('.', 1)[0]
            # Get the first integer
            first_int = int(name_without_ext.split('-')[0])
            
            # Add newline if first int changed (but not before the very first item)
            if prev_first_int is not None and first_int != prev_first_int:
                result.append('\n')
            
            result.append(s)
            prev_first_int = first_int
        
        return result
    
    pixels = sort_dash_separated(order)
    pixels = add_newlines_on_first_int_change(pixels)
    pixels = list(map(measure_darkness_opencv, pixels))
    

    # Replace each pixel with the associated ascii character with it
    tile_library = [
        "$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", 
        "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", 
        "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", 
        "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", 
        "^", "`", "'", "."
    ]

    # Map darkness values (0-255) to ASCII characters
    min_pixel = min([p for p in pixels if isinstance(p, (float))])
    max_pixel = max([p for p in pixels if isinstance(p, (float))])
    ascii_chars = [tile_library[int((p - min_pixel) / (max_pixel - min_pixel) * (len(tile_library) - 1))] if isinstance(p, (int, float)) else p for p in pixels]

    # Create the final image
    final_string = "".join(ascii_chars)

    # Cleanup middle folders
    def remove_images(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) # Remove file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) # Remove directory and contents
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        os.rmdir(folder)

    remove_images("middle")
    remove_images("middle2")
    
    # Return the final image
    return final_string



if __name__ == "__main__":
    image_path = sys.argv[1]
    height, width = int(sys.argv[2]), int(sys.argv[3])
    print(img_to_ascii(image_path=image_path, height=height, width=width))
