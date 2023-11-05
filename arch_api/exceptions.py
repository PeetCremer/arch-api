import fastapi
from bson.errors import InvalidId


class SplittingError(Exception):
    ...


async def splitting_error_handler(_: fastapi.Request, exc: SplittingError) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def invalid_object_id_handler(_: fastapi.Request, exc: InvalidId) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
