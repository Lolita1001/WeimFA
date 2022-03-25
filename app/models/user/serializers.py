from typing import Optional, List

from models.user.base import UserBase, MediaUserBase

from models.user.schemes import MediaUser, User
from models.dog.schemes import Dog


class UserResponse(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: str
    updated_at: str | None
    media: Optional[List["MediaUser"]]
    dog_owner: Optional[List["Dog"]]
    dog_breeder: Optional[List["Dog"]]


class MediaUserResponse(MediaUserBase):
    id: int
    created_at: str
    user: Optional["User"]  # TODO почему не могу заменить на UserResponse?


UserResponse.update_forward_refs()
MediaUserResponse.update_forward_refs()
