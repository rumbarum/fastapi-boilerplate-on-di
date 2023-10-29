from typing import Any

import orjson
from fastapi.responses import JSONResponse


def json_encoder_extend(obj):
    return str(obj)


class CustomORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed"
        return orjson.dumps(
            content, default=json_encoder_extend, option=orjson.OPT_INDENT_2
        )
