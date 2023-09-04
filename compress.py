from PIL import Image
from pillow_heif import register_heif_opener
import datetime
from PIL.ExifTags import TAGS

def compress_image(input_path, output_path, quality = 80):
    try:
        register_heif_opener()
        image = Image.open(input_path)
        # Save the image as WebP with specified quality
        image.thumbnail((960,720))
        image.save(output_path, format="WebP", quality=quality)
        print(f"Image compressed and saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

def getImageDATETIME(i_path):
    register_heif_opener()
    i = Image.open(i_path)
    info = i.getexif()
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(info)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%')
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "DateTimeOriginal":
            print(f"The image was taken on {value}")
            return value
def convertDate(date):
    # Define the input and output formats
    input_format = "%Y:%m:%d %H:%M:%S"
    output_format = "%d-%m-%y"

    # Convert the input datetime string to a datetime object
    input_datetime = datetime.datetime.strptime(date, input_format)

    # Convert the datetime object to the desired output format
    return input_datetime.strftime(output_format)