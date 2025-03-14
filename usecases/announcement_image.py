import io
import uuid
from typing import List

import PIL.Image
import requests

import config
import watermark_remove
from FtpUploader import FtpUploader
from models import FailedImageUploads
from usecases import usecase_logger, session

conf = config.Config()
HOST = conf.get('FTP.Host')
USERNAME = conf.get('FTP.Username')
PASSWORD = conf.get('FTP.Password')

ftp_client = FtpUploader(HOST, USERNAME, PASSWORD)


def upload(image_list: List[str], announcement_id: uuid.UUID) -> List[str]:
    uploaded_images: List[str] = []
    for index, image_link in enumerate(image_list):
        response = requests.get(image_link, stream=True)
        image_bytes = io.BytesIO(response.content)
        image = PIL.Image.open(image_bytes)

        processed_image = watermark_remove.remove_beetenders_by_color(image)

        try:
            upload_path = f"images/{announcement_id.hex}_{index}.jpg"
            ftp_client.upload_file_b(processed_image, upload_path)
            uploaded_images.append(upload_path)
        except Exception:
            failed_image = FailedImageUploads(image_link=image_link, announcement_id=announcement_id)
            session.add(failed_image)
            return []

    return uploaded_images
