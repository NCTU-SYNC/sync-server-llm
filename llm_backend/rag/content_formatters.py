from collections.abc import Callable, Sequence
from enum import StrEnum


class ContentFormat(StrEnum):
    PLAIN = "plain"
    NUMBERED = "numbered"


ContentFormatter = Callable[[Sequence[str]], Sequence[str]]

CONTENT_FORMATTERS: dict[ContentFormat, ContentFormatter] = {
    ContentFormat.PLAIN: lambda x: x,
    ContentFormat.NUMBERED: lambda x: [
        f"{i}. {line}" for i, line in enumerate(x, start=1)
    ],
}
