from flask import Flask

from .flask_uploads import UploadSet, IMAGES
from .flask_uploads import configure_uploads

# photos = UploadSet('photos', IMAGES)

# Add support for TIF/TIFF files
photos = UploadSet('photos', IMAGES + ('tif', 'tiff', 'TIF', 'TIFF'))



def init_upload(app: Flask):
    configure_uploads(app, photos)
