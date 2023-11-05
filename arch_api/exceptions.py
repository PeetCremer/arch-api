import fastapi


class SplittingError(Exception):
    ...


async def splitting_error_handler(_: fastapi.Request, exc: SplittingError) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


HANDLERS = {
    SplittingError: splitting_error_handler,
}
