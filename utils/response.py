from typing import Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from utils.constant import ERROR_BAD_REQUEST, SUCCESS

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true',
}


def response(data: Optional[Union[Dict, List]], success: bool, message: Optional[str], status_code: int,
             errors: Optional[Union[Dict, List]] = None, warning: Optional[str] = None, **kwargs):
    content = {
        "message": message,
        "success": success,
        "data": data,
    }

    if success:
        content["warning"] = warning
    else:
        content["errors"] = errors

    return JSONResponse(
        content=jsonable_encoder(content, **kwargs),
        status_code=status_code,
        headers=headers
    )


def success(status_code=SUCCESS, message: Optional[str] = None, data: Optional[Union[Dict, List]] = None,
            warning: Optional[str] = None, **kwargs):
    return response(data=data, success=True, message=message, status_code=status_code,
                    warning=warning, **kwargs)


def error(status_code=ERROR_BAD_REQUEST, message: Optional[str] = None,
          errors: Optional[dict] = None, data: Optional[Union[Dict, List]] =None , **kwargs):
    return response(data=data, success=False, message=message, status_code=status_code,
                    errors=errors, **kwargs)
