from pydantic import BaseModel, Field, HttpUrl


class AuditRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="The HTTP or HTTPS URL to audit",
    )


class AuditResponse(BaseModel):
    request_id: str
    url: str
    status: str
    cached: bool
    audit: dict