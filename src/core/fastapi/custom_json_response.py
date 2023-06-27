from typing import Any

import numpy as np
import orjson
from fastapi.responses import JSONResponse
from pandas import Timestamp


def json_encoder_extend(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Timestamp):
        return obj.timestamp()
    return str(obj)


class CustomORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed"
        return orjson.dumps(
            content, default=json_encoder_extend, option=orjson.OPT_INDENT_2
        )
