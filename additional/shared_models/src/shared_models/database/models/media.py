from tortoise import Model, fields
from .message import Message


class Media(Model):
    id = fields.IntField(pk=True)
    message: fields.OneToOneRelation[Message] = fields.OneToOneField(
        "models.Message",
        related_name="media",
        on_delete=fields.CASCADE,
    )
    url = fields.CharField(max_length=2048)
    created_at = fields.DatetimeField(auto_now_add=True)
