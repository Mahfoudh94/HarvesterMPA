import ftplib
import io
import os.path
from abc import ABC


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
    def __init__(self, host):
        self.client = ftplib.FTP(host)
        self.client.voidcmd("NOOP")  # Initial NOOP to check the connection.

    def keep_connection_alive(self):
        try:
            self.client.voidcmd("NOOP")  # Keeps the connection alive.
        except (ftplib.error_temp, ftplib.error_perm):
            self.client.close()
            self.client.connect()

    def login(self, username, password):
        self.client.login(username, password)

    def upload_file_b(self, file, remote_path):
        self.keep_connection_alive()
        self.client.storbinary(f"STOR {remote_path}", file)

    def upload_binary(self, payload, remote_path):
        self.keep_connection_alive()
        with io.BytesIO(payload) as file_obj:
            self.client.storbinary(f"STOR {remote_path}", file_obj)

    def quit(self):
        self.client.quit()
