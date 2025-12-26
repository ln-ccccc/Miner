# import os
# import os.path as osp
# import uuid

# from flask import current_app
# from sqlalchemy import desc

# from applications.common.curd import model_to_dicts
# from applications.extensions import db
# from applications.extensions.init_upload import photos
# from applications.models import Photo
# from applications.schemas import PhotoOutSchema


# def get_photo(page, limit):
#     photo = Photo.query.order_by(desc(Photo.create_time)).paginate(
#         page=page, per_page=limit, error_out=False)
#     count = Photo.query.count()
#     data = model_to_dicts(schema=PhotoOutSchema, data=photo.items)
#     return data, count


# def upload_one(photo, mime, type_=0):
#     filename = photos.save(photo, name=str(uuid.uuid4()) + ".")
#     file_url = '/_uploads/photos/' + filename
#     # file_url = photos.url(filename)
#     upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
#     size = os.path.getsize(upload_url + '/' + filename)
#     photo = Photo(
#         name=filename, href=file_url, mime=mime, size=size, type=type_)
#     db.session.add(photo)
#     db.session.commit()
#     return file_url, photo.id


# def delete_photo_by_id(_id):
#     photo_name = Photo.query.filter_by(id=_id).first().name
#     photo = Photo.query.filter_by(id=_id).delete()
#     db.session.commit()
#     upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
#     os.remove(upload_url + '/' + photo_name)
#     return photo


# def img_url_handle(url):
#     return osp.basename(url)
#     # return url[url.rfind("/") + 1:len(url)]


import os
import os.path as osp
import uuid
import cv2  # 新增
import numpy as np # 新增

from flask import current_app
from sqlalchemy import desc

from applications.common.curd import model_to_dicts
from applications.extensions import db
from applications.extensions.init_upload import photos
from applications.models import Photo
from applications.schemas import PhotoOutSchema


def get_photo(page, limit):
    photo = Photo.query.order_by(desc(Photo.create_time)).paginate(
        page=page, per_page=limit, error_out=False)
    count = Photo.query.count()
    data = model_to_dicts(schema=PhotoOutSchema, data=photo.items)
    return data, count


def upload_one(photo, mime, type_=0):
    # 生成唯一文件名
    ext = os.path.splitext(photo.filename)[1].lower()
    name_uuid = str(uuid.uuid4())
    filename = name_uuid + ext
    
    # 保存原始文件
    filename = photos.save(photo, name=filename)
    
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    file_path = os.path.join(upload_url, filename)
    
    # 检查是否为 TIF/TIFF，如果是，生成 PNG 用于显示
    if ext in ['.tif', '.tiff']:
        try:
            # 读取 TIF
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # 简单的归一化/转换到 8位 用于显示
                if img.dtype != np.uint8:
                    # 简单压缩到 0-255
                    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
                    img = img.astype(np.uint8)
                
                # 如果是多波段，只取前3个
                if len(img.shape) == 3 and img.shape[2] > 3:
                    img = img[:, :, :3]
                
                # 保存为 PNG
                png_filename = name_uuid + ".png"
                png_path = os.path.join(upload_url, png_filename)
                cv2.imwrite(png_path, img)
                
                # 更新返回给前端的文件名为 PNG
                # 注意：这里我们让前端看到的是 PNG，后端数据库存的也是 PNG 的链接
                # 这样前端就能正常显示了
                # 原始 TIF 仍然保留在磁盘上（filename），但数据库指向 PNG
                filename = png_filename
                mime = 'image/png'
        except Exception as e:
            print(f"Error converting TIF to PNG: {e}")
            # 如果转换失败，回退到原始文件（虽然前端可能显示不了）

    file_url = '/_uploads/photos/' + filename
    # file_url = photos.url(filename)
    
    # 获取最终文件（可能是 PNG）的大小
    final_path = os.path.join(upload_url, filename)
    size = os.path.getsize(final_path)
    
    photo = Photo(
        name=filename, href=file_url, mime=mime, size=size, type=type_)
    db.session.add(photo)
    db.session.commit()
    return file_url, photo.id


def delete_photo_by_id(_id):
    photo_name = Photo.query.filter_by(id=_id).first().name
    photo = Photo.query.filter_by(id=_id).delete()
    db.session.commit()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    try:
        os.remove(upload_url + '/' + photo_name)
    except:
        pass
    return photo


def img_url_handle(url):
    return osp.basename(url)
    # return url[url.rfind("/") + 1:len(url)]