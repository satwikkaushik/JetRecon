"""Middleware to handle custom errors and exceptions globally"""

import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

from utils.errors import AppError


class ErrorHandlerMiddleware:
    """Middleware to handle exceptions globally and return consistent error responses."""

    def __init__(self, app, show_traceback: bool = False):
        self.app = app
        self.show_traceback = show_traceback

    async def __call__(self, scope, receive, send):

        # non-http requests are passed through
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        try:
            response = await self.app(scope, receive, send)
            return response
        except AppError as ae:
            # Handle custom application errors

            payload = ae.to_dict()
            if self.show_traceback:
                payload["traceback"] = traceback.format_exc()

            response = JSONResponse(
                status_code=ae.status_code,
                content=payload,
            )

            await response(scope, receive, send)
        except Exception as e:
            # Handle unexpected errors

            payload = {
                "error": "InternalServerError",
                "message": "An unexpected error occurred.",
                "details": str(e),
            }

            if self.show_traceback:
                payload["traceback"] = traceback.format_exc()

            response = JSONResponse(
                status_code=500,
                content=payload,
            )

            await response(scope, receive, send)
