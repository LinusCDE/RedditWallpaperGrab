#!/usr/bin/env python3

from PIL import Image
from PIL import ImageFilter


class ImageTooSmallExecption (Exception):
    '''Raised if image is smaller than allowed (defined via --min-size)'''
    pass


def resize_image(image, width=-1, height=-1):
    '''Resize image; auto-determine size for missing dimension'''
    if width == -1 and height == -1:
        return image

    img_width, img_height = image.size

    if width == -1:
        width = (img_width * height) // img_height
    elif height == -1:
        height = (img_height * width) // img_width

    return image.resize((width, height), Image.ANTIALIAS)


def blurImage(image, radius=5):
    '''Apply blur-filter to image'''
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def offset(frame_size, image_size):
    '''Get offset to fit image centered into frame'''
    if len(frame_size) is not 2 or len(image_size) is not 2:
        return None
    x_offset = (frame_size[0] // 2) - (image_size[0] // 2)
    y_offset = (frame_size[1] // 2) - (image_size[1] // 2)
    return (x_offset, y_offset)


def create_wallpaper(
        img_input_path, img_output_path, ta_size, allow_blur, min_size=None):
    '''Convert image to fit the target size and can check for minimum size'''
    img = Image.open(img_input_path)

    bg = Image.new('RGBA', (ta_size), (0, 0, 0, 0))
    width, height = img.size

    if min_size and (width < min_size[0] or height < min_size[1]):
        raise ImageTooSmallExecption()

    pasted_image, blurred_background = None, None

    if width > height:  # Landscape
        pasted_image = resize_image(img, width=ta_size[0])
        blurred_background = resize_image(img, height=ta_size[1])
    else:  # Portrait or Squared
        pasted_image = resize_image(img, height=ta_size[1])
        blurred_background = resize_image(img, width=ta_size[0])

    if allow_blur:
        blurredBackground = blurImage(blurred_background, radius=50)
    bg.paste(blurredBackground, offset(ta_size, blurredBackground.size))
    bg.paste(pasted_image, offset(ta_size, pasted_image.size))

    bg.save(img_output_path)
