import inspect

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseConfig, BaseModel, ValidationError

from application.core.utils.camelcase import snake2camel


class ResponseBaseModel(BaseModel):
    class Config(BaseConfig):
        alias_generator = snake2camel
        allow_population_by_field_name = True
        orm_mode = True


class BodyBaseModel(BaseModel):
    class Config(BaseConfig):
        alias_generator = snake2camel


class FormBaseModel(BaseModel):
    def __init_subclass__(cls, *args, **kwargs):
        field_default = Form(...)
        new_params = []
        for field in cls.__fields__.values():
            default = Form(field.default) if not field.required else field_default
            annotation = inspect.Parameter.empty

            new_params.append(
                inspect.Parameter(
                    field.alias,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=default,
                    annotation=annotation,
                )
            )

        async def _as_form(**data):
            try:
                return cls(**data)
            except ValidationError as e:
                raise RequestValidationError(e.raw_errors)

        sig = inspect.signature(_as_form)
        sig = sig.replace(parameters=new_params)
        _as_form.__signature__ = sig  # type: ignore
        setattr(cls, "as_form", _as_form)

    @staticmethod
    def as_form(parameters: list) -> "FormBaseModel":
        raise NotImplementedError

    class Config(BaseConfig):
        alias_generator = snake2camel
