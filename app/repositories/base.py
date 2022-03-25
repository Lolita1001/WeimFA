import os
import shutil

from fastapi import UploadFile, status
from sqlmodel import select
from uuid import uuid4

from db.database import Session
from db.utils.exceptions import HTTPExceptionCustom as HTTPException


class BaseRepository:
    def __init__(self, session: Session):
        self.session = session
        self.AVAILABLE_MEDIA_EXTENSIONS = ['.jpg', '.png']

    @staticmethod
    def check_required_field(model):
        required_field_names = [field_name for field_name, field_value in model.__fields__.items() if
                                field_value.field_info.extra.get("c_required", False)]
        empty_required_fields = [required_field_name for required_field_name in
                                 required_field_names
                                 if not model.__getattribute__(required_field_name)]
        return required_field_names, empty_required_fields

    @staticmethod
    def remove_files(path_files: str | list[str]):
        path_files = [path_files] if isinstance(path_files, str) else path_files
        for path_file in path_files:
            if os.path.exists(path_file):
                os.remove(path_file)

    def save_file(self, in_file: UploadFile, path: str):
        in_filename, in_ext = os.path.splitext(in_file.filename)
        if in_ext not in self.AVAILABLE_MEDIA_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Unsupported file type. Support {', '.join(self.AVAILABLE_MEDIA_EXTENSIONS)}")
        filename = uuid4().__str__()
        file_path = path + filename + in_ext
        in_file.file.seek(0, os.SEEK_END)
        file_length = in_file.file.tell()
        in_file.file.seek(0, os.SEEK_SET)
        if file_length > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=status.HTTP_411_LENGTH_REQUIRED,
                                detail=f"Media is too large ({file_length / 1024 / 1024}MB), 5MB max.")
        with open(file_path, 'wb') as out_file:
            try:
                shutil.copyfileobj(in_file.file, out_file)
            except Exception as ex:  # TODO уточнить необходимый тип исключения
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Failed to save file")
            finally:
                in_file.file.close()
        return file_path

    def check_have_main_media(self, model):
        db_media = self.session.exec(select(model).where(model.is_main)).first()
        return False if db_media else True
