import uuid
from typing import List

import cv2
import numpy as np
import requests

import config
import watermark_remove
from FtpUploader import FtpUploader

conf = config.Config()
HOST = conf.get('FTP.Host')
USERNAME = conf.get('FTP.Username')
PASSWORD = conf.get('FTP.Password')

ftp_client = FtpUploader(HOST)
ftp_client.login(USERNAME, PASSWORD)


def upload(image_list: List[str], announcement_id: uuid.UUID) -> List[str]:
    uploaded_images: List[str] = []
    for index, image in enumerate(image_list):
        # Fetch the image from the URL
        response = requests.get(image, stream=True)
        response.raise_for_status()
        image_data = np.frombuffer(response.content, np.uint8)
        image_np = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        # Process the image with watermark remover
        processed_image = watermark_remove.remove_beetender(image_np)

        # Upload the processed image
        upload_path = f"images/{announcement_id.hex}_{index}.jpg"
        ftp_client.upload_file_b(processed_image, upload_path)
        uploaded_images.append(upload_path)

    return uploaded_images
