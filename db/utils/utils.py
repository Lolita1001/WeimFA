import os
import shutil

from fastapi import UploadFile, HTTPException, status
from uuid import uuid4

AVAILABLE_MEDIA_EXTENSIONS = ['.jpg', '.png']


def save_file(in_file: UploadFile, path: str):
    in_filename, in_ext = os.path.splitext(in_file.filename)
    if in_ext not in AVAILABLE_MEDIA_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unsupported file type. Support {', '.join(AVAILABLE_MEDIA_EXTENSIONS)}")
    filename = uuid4().__str__()
    file_path = path + filename + in_ext
    in_file.file.seek(0, os.SEEK_END)
    file_length = in_file.file.tell()
    if file_length > 5*1024*1024: #  5MB
        raise HTTPException(status_code=status.HTTP_411_LENGTH_REQUIRED,
                            detail=f"Media is too large ({file_length/1024/1024}MB), 5MB max.")
    with open(file_path, 'wb') as out_file:
        try:
            shutil.copyfileobj(in_file.file, out_file)
        except Exception as ex:  # TODO уточнить необходимый тип исключения
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to save file")
        finally:
            in_file.file.close()
    return file_path
