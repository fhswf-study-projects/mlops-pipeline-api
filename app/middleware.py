"""Functionality checking bearer token on each request for predefined endpoints.
In case the bearer token is not provided or invalid. Unauthorized HTTPException will be thrown."""

import os
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.constants import EnvConfig


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> None:
    if not credentials.credentials:
        logger.exception("Unauthorized access. No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Expected bearer token.",
        )
    token = credentials.credentials.split()[-1]
    expected_token = os.environ[EnvConfig.API_BEARER_TOKEN.value]

    if expected_token != token:
        logger.exception("Unauthorized access. Provided token invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Provided bearer token invalid.",
        )
