from fastapi.responses import JSONResponse


def api_response(status_code: int, success: int, message: str,error_code: str | None = None, data: dict | list | None = None,):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "error_code": error_code,
            "data": data,
        },
    )