from ....base import MaxObject
from pydantic import Field


class ContactAttachmentRequestPayload(MaxObject):
    name: str | None = Field(None, description="Name of the contact")
    contact_id: int | None = Field(None, description="ID of the contact")
    vcf_info: str | None = Field(None, description="User info in VCF format")
    vcf_phone: str | None = Field(None, description="Phone number in VCF format")
