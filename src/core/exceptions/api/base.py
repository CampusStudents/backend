from starlette.responses import JSONResponse


class InternalServerException:
    @staticmethod
    def response():
        return JSONResponse(
            content={"detail": "Internal server error"}, status_code=500
        )
