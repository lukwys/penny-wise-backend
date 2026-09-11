from app.exceptions import OcrError, ParsingError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .routers.auth import auth_router
from .routers.expenses import expenses_router

app = FastAPI()


CONSTRAINT_MESSAGES = {
    "user_email_key": "Email already used",
    "fallback": "Database constraint violated",
}

@app.exception_handler(IntegrityError)
def integrity_exepction_handler(_request: Request, exc: IntegrityError):
    error_code = int(exc.orig.pgcode)
    if error_code == 23505:
        return JSONResponse(
            status_code=409,
            content={
                "message": CONSTRAINT_MESSAGES.get(
                    exc.orig.diag.constraint_name, CONSTRAINT_MESSAGES["fallback"]
                )
            },
        )
    if error_code == 23502:
        return JSONResponse(
            status_code=422, content={"message": "Missing required field"}
        )
    return JSONResponse(
        status_code=500, content={"message": CONSTRAINT_MESSAGES["fallback"]}
    )


@app.exception_handler(OcrError)
def ocr_exception_handler(_request: Request, exc: OcrError):
    return JSONResponse(status_code=422, content={"message": str(exc)})


@app.exception_handler(ParsingError)
def parsing_exception_handler(_request, exc: ParsingError):
    return JSONResponse(status_code=502, content={"message": str(exc)})

app.include_router(auth_router)
app.include_router(expenses_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

