from ....base import MaxObject
from ...user import User
from pydantic import Field


class ContactAttachmentPayload(MaxObject):
    vcf_info: str | None = Field(None, description="User info in VCF format")
    max_info: User | None = Field(None, description="User info")
