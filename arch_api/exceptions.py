import fastapi
from bson.errors import InvalidId


class SplittingError(Exception):
    """
    Error originating from geometries that cannot be split
    """

    ...


async def splitting_error_handler(_: fastapi.Request, exc: SplittingError) -> fastapi.responses.JSONResponse:
    """
    Transforms a SplittingError into a BAD_REQUEST response
    """
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def invalid_object_id_handler(_: fastapi.Request, exc: InvalidId) -> fastapi.responses.JSONResponse:
    """
    Transforms a bson InvalidId error into a BAD_REQUEST response
    """
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
