import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from app.exceptions.fetch_exceptions import (
    ConnectionFailedError,
    FetchTimeoutError,
)
from app.schemas.audit import AuditRequest, AuditResponse
from app.services.cache_service import get_cached, set_cached
from app.services.fetch_service import fetch_url
from app.services.rate_limit_service import check_rate_limit


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/audits",
    tags=["Audits"],
)


@router.post("", response_model=AuditResponse)
async def create_audit(
    payload: AuditRequest,
    request: Request,
) -> AuditResponse:
    request_id = str(uuid4())

    client_id = request.client.host if request.client else "unknown"

    if not check_rate_limit(client_id):
        logger.warning(
            "rate_limit_exceeded request_id=%s client_id=%s",
            request_id,
            client_id,
        )

        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "request_id": request_id,
            },
        )

    url = str(payload.url)

    logger.info(
        "audit_started request_id=%s url=%s",
        request_id,
        url,
    )

    cached_result = await get_cached(url)

    if cached_result is not None:
        logger.info(
            "audit_cache_hit request_id=%s url=%s",
            request_id,
            url,
        )

        return AuditResponse(
            request_id=request_id,
            url=url,
            status="completed",
            cached=True,
            audit=cached_result,
        )

    try:
        result = await fetch_url(url)

    except FetchTimeoutError as exc:
        logger.warning(
            "audit_timeout request_id=%s url=%s",
            request_id,
            url,
        )

        raise HTTPException(
            status_code=504,
            detail={
                "code": "FETCH_TIMEOUT",
                "message": str(exc),
                "request_id": request_id,
            },
        ) from exc

    except ConnectionFailedError as exc:
        logger.warning(
            "audit_connection_failed request_id=%s url=%s",
            request_id,
            url,
        )

        raise HTTPException(
            status_code=502,
            detail={
                "code": "CONNECTION_FAILED",
                "message": str(exc),
                "request_id": request_id,
            },
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_TARGET_URL",
                "message": str(exc),
                "request_id": request_id,
            },
        ) from exc

    except Exception as exc:
        logger.exception(
            "audit_failed request_id=%s url=%s",
            request_id,
            url,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Unexpected server error.",
                "request_id": request_id,
            },
        ) from exc

    audit_result = {
        "status_code": result.status_code,
        "response_time_ms": result.response_time_ms,
        "content_type": result.content_type,
        "content_length": result.content_length,
    }

    await set_cached(
        key=url,
        value=audit_result,
    )

    logger.info(
        "audit_completed request_id=%s url=%s status_code=%s response_time_ms=%s",
        request_id,
        url,
        result.status_code,
        result.response_time_ms,
    )

    return AuditResponse(
        request_id=request_id,
        url=url,
        status="completed",
        cached=False,
        audit=audit_result,
    )