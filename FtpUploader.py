import ftplib
import io
import os.path
import logger
import logging
from abc import ABC

ftp_logger = logging.getLogger("FTP")

class FtpUploadAbstract(ABC):
    def login(self, username, password):
        pass

    def upload_file_b(self, file, remote_path):
        pass

    def upload_file_from_path(self, file_path, remote_folder):
        remote_path = os.path.join(
                remote_folder,
                os.path.basename(file_path))\
            .replace('\\', '/')
        with open(file_path, 'rb') as file:
            self.upload_file_b(file, remote_path)

    def quit(self):
        pass


class FtpUploader(FtpUploadAbstract):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.client = ftplib.FTP()
        self.connect()

    def connect(self):
        self.client.connect(self.host)
        response = self.client.login(self.username, self.password)
        ftp_logger.info(f'Login returned: {response}')

    def keep_connection_alive(self):
        try:
            self.client.pwd()  # Keeps the connection alive.
        except (ftplib.error_temp, ftplib.error_perm, ConnectionAbortedError):
            self.connect()

    def upload_file_b(self, file, remote_path):
        self.keep_connection_alive()
        try:
            response_code = self.client.storbinary(f"STOR {remote_path}", file)
            ftp_logger.info(f"Upload to {remote_path} got: {response_code}")
        except (ftplib.error_temp, ftplib.error_perm) as e:
            ftp_logger.error(f"Upload to {remote_path} got: {e}")
            raise Exception
        except Exception as e:
            ftp_logger.error(f"Upload to {remote_path} got: {e.__class__.__name__}: {e}")
            raise Exception

    def upload_binary(self, payload, remote_path):
        self.keep_connection_alive()
        with io.BytesIO(payload) as file_obj:
            self.client.storbinary(f"STOR {remote_path}", file_obj)

    def quit(self):
        self.client.quit()
