import os.path
import shutil

from fastapi import UploadFile
from uuid import uuid4


def save_file(in_file: UploadFile, path: str):
    filename = f"{uuid4()}{os.path.splitext(in_file.filename)[1]}"
    file_path = path + filename
    with open(file_path, 'wb') as out_file:
        try:
            shutil.copyfileobj(in_file.file, out_file)
        except Exception as ex:  # TODO уточнить необходимый тип исключения
            return None
        finally:
            in_file.file.close()
    return file_path
