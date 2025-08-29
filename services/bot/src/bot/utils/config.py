import os
from dotenv import load_dotenv
from typing import Final
from zoneinfo import ZoneInfo

load_dotenv()


class Config:
    """Service configuration class."""

    TIME_ZONE: Final[ZoneInfo] = ZoneInfo(os.getenv("TIME_ZONE", "Europe/Moscow"))
    # RabbitMQ configuration
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # PostgreSQL configuration
    POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: Final[int] = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB", "")

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_STORAGE_DB: Final[int] = int(os.getenv("REDIS_STORAGE_DB", 0))

    # Secrets
    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
    NAME_API_KEY: Final[str] = os.getenv("NAME_API_KEY", "")

    # Other configurations
    ALLOWED_CHARACTERS: Final[str] = os.getenv(
        "ALPHABET",
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123456789!@#$&()-=_;:'\",.?|`№ "
        "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥳🤩🥸😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢"
        "😭😤😠😡🤯😳🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴😪😵🤐🥴🤧😷🤒🤕🤑🤠😈👿👹👺👻👽👾"
        "🤖🎃😺😸😹😻😼😽🙀😿😾🙌👏🤝👍👎👊✊🤛🤜🤞✌️🤟🤘🤙👈👉👆👇☝️✋🤚🖐🖖👋🤙🤚👐🤲🤝🙏💪🦾🦿🦵🦶"
        "👂👃👣👀🧠🦷🦴👅👄💋👓🕶🥽🥼🦺👔👕👖🧣🧤🧥🧦👗👘🥻🩱🩲🩳👙👚👛👜👝🎒👞👟🥾🥿👠👡🩰👢👑👒🎩🎓"
        "🧢⛑💄💍💼🧳🌂☂️🧵🧶👶🧒👦👧🧑👨👩🧓👴👵🙍🙎🙅🙆💁🙋🧏🙇🤦🤷💆💇🚶🏃💃🕺🧖🧗🧘🏇🏂🏌️‍♂️🏄🚣🏊🤽"
        "🚴🚵🏇🧍🧎🏋️‍♂️🤸🤼🤽‍♀️🤾🤹🧑‍🎄🧙‍♂️🧚🧛🧜🧝🧞🧟🐶🐱🐭🐹🐰🦊🐻🐼🐻‍❄️🐨🐯🦁🐮🐷🐸🐵🦄🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇"
        "🐺🐗🐴🦓🦌🦄🐝🐛🦋🐌🐞🐜🦗🕷🕸🦂🦟🦠🐢🐍🦎🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🦧🦥🦦🦨🦡🦃🐓🐕🐩🐈🐇🐿"
        "🦔🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🥑🥔🥕🌽🌶🥒🥬🥦🧄🧅🥜🌰🍞🥐🥖🥨🥯🥞🧇🥩🍗🍖🥓🍔🍟🍕🌭"
        "🥪🌮🌯🥙🧆🥚🍳🥘🍲🥗🥫🍿🧈🥫🥤🧃🧉🍵☕🧊🧉🍾🧁🍰🎂🍮🍩🍪🎃🎄🎆✨🎉🎊🎈🎁🎗🎟🎫🎖🏆🏅🎮🎲🎯🎳🧩"
        "🧸🎭🎨🎬🎤🎧🎼🎹🥁🎷🎺🎸🪕🎻🎬🛹🛷⛷🏂🏋️‍♀️🤺🤼‍♂️🤸‍♀️🏇🏄‍♂️🧗‍♀️🚣‍♂️🏊‍♀️🤽‍♂️🚴‍♀️🚵‍♂️🏍🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🚚🚛🚜🛴🛵"
        "🏍️🚲🛺🚨🚥🚦🛑🚧⚓⛵🚤🛳⛴🛥🚢✈️🛩️🛫🛬🚀🛸🛎️🧳⏰🕰️⌛⏳📅📆🗓️📇📈📉📊📋📌📍📎🖇️📏📐✂️🖊️🖋📝"
        "🩷❤🧡💛💚🩵💙💜🖤🩶🤍🤎💔❤‍🔥❤‍🩹❣💕💞💝💘💖💗💓",
    )
    MAX_MESSAGE_LENGTH: Final[int] = int(os.getenv("MAX_MESSAGE_LENGTH", 80))
    MAX_NAME_LENGTH: Final[int] = int(os.getenv("MAX_NAME_LENGTH", 15))
    MAX_CITY_LENGTH: Final[int] = int(os.getenv("MAX_CITY_LENGTH", 15))
    MINIMAL_NAME_CONFIDENCE: Final[float] = float(
        os.getenv("MINIMAL_NAME_CONFIDENCE", 0.6)
    )
    TERMS_OF_USE_URL: Final[str] = os.getenv(
        "TERMS_OF_USE_URL", "https://example.com/terms-of-use"
    )
    PROCESSING_OF_PERSONAL_DATA_URL: Final[str] = os.getenv(
        "PROCESSING_OF_PERSONAL_DATA_URL",
        "https://example.com/processing-of-personal-data",
    )
    MESSAGE_COLLECTION_STOPPED: Final[bool] = (
        os.getenv("MESSAGE_COLLECTION_STOPPED", "0").lower() == "1"
    )
    MESSAGES_TIME_OUT_MINUTES: Final[int] = int(
        os.getenv("MESSAGES_TIME_OUT_MINUTES", 1)
    )
    MAXIMUM_MESSAGES_PER_USER: Final[int] = int(
        os.getenv("MAXIMUM_MESSAGES_PER_USER", 2)
    )
    MAXIMUM_ATTEMPTS_PER_MESSAGE: Final[int] = int(
        os.getenv("MAXIMUM_ATTEMPTS_PER_MESSAGE", 3)
    )
    START_MESSAGE_IMAGE_TOKEN: Final[str | None] = os.getenv(
        "START_MESSAGE_IMAGE_TOKEN"
    )
    START_MESSAGE_IMAGE_ID: Final[int] = os.getenv("START_MESSAGE_IMAGE_ID", '+0j1rPUs1H65/7ZKMhu76Bo+pAIoMVIpwX99/nRI2gA3F57In52ZPg')
    START_MESSAGE_IMAGE_URL: Final[str] = os.getenv("START_MESSAGE_IMAGE_ID", '')

    COORDINATE_EXTRACTOR_URL: Final[str] = os.getenv(
        "COORDINATE_EXTRACTOR_URL", "https://nominatim.openstreetmap.org/reverse"
    )

    NAME_API_URL: Final[str] = os.getenv(
        "NAME_API_URL", "https://api.nameapi.org/rest/v5.3/parser/personnameparser"
    )
    CITIES_SERVICE_URL: Final[str] = os.getenv(
        "CITIES_SERVICE_URL", "http://cities:8080"
    )
    IS_TESTING: Final[bool] = os.getenv("IS_TESTING", "0").lower() == "1"

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN environment variable is not set")

    if NAME_API_KEY == "":
        raise ValueError("NAME_API_KEY environment variable is not set")

    if POSTGRES_USER == "":
        raise ValueError("POSTGRES_USER environment variable is not set")

    if POSTGRES_PASSWORD == "":
        raise ValueError("POSTGRES_PASSWORD environment variable is not set")

    if POSTGRES_DB == "":
        raise ValueError("POSTGRES_DB environment variable is not set")

    # Webhook configuration
    WEBHOOK_HOST: Final[str] = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT: Final[int] = int(os.getenv("WEBHOOK_PORT", 16384))
