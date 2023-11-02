import fastapi

app = fastapi.FastAPI(
    title="Architecture API (arch-api)",
    description=(
        "Consumes building limits and height plateaus, splits up the building limits"
        "according to the height plateaus, and stores these three entities persistently"
    ),
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"health": "OK"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=8000, reload=True)
