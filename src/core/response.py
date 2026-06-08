from fastapi.responses import JSONResponse


def success_response(message: str, data=None):
    return JSONResponse(
        {
            "success": True,
            "message": message,
            "data": data
        }
    )


def error_response(message: str):
    return JSONResponse(
        {
            "success": False,
            "message": message,
            "data": None
        }
    )