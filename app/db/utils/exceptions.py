from typing import Any, Optional, Dict

from fastapi import HTTPException


class HTTPExceptionCustom(HTTPException):
    def __init__(self,
                 status_code: int,
                 detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None
                 ):
        super().__init__(status_code=status_code, detail=detail)
        self.headers = {"custom_exc": "True"}
        if headers:
            [self.headers.__setitem__(key, value) for key, value in headers.items()]
