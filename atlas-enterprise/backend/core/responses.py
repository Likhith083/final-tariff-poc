from fastapi.responses import JSONResponse
from typing import Any, Optional

def success_response(data: Any = None, message: str = "Success", **kwargs) -> JSONResponse:
    resp = {"success": True, "message": message, "data": data}
    resp.update(kwargs)
    return JSONResponse(content=resp)

def error_response(message: str = "Error", error_code: Optional[str] = None, details: Any = None, status_code: int = 400, **kwargs) -> JSONResponse:
    resp = {"success": False, "message": message, "error_code": error_code, "details": details}
    resp.update(kwargs)
    return JSONResponse(content=resp, status_code=status_code) 