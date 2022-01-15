from __future__ import annotations

from slack_sdk.models.blocks.basic_components import MarkdownTextObject
from slack_sdk.models.blocks.blocks import (
    SectionBlock,
    ContextBlock,
    HeaderBlock,
)
from slack_sdk.models.blocks.blocks import (
    ContextBlock,
    DividerBlock,
)


def header(text: str | None) -> HeaderBlock | None:
    if text:
        return HeaderBlock(text=text, block_id="header")


def text(text: str | None) -> SectionBlock | None:
    if text:
        return SectionBlock(block_id="text", text=MarkdownTextObject(text=text))


def context(context: list = None) -> list[DividerBlock | ContextBlock]:
    if context:
        return [
            DividerBlock(),
            ContextBlock(
                block_id="context",
                elements=[MarkdownTextObject(text=element) for element in context],
            ),
        ]
    return []


def operation(
    name: str, status: str, started: str, finished: str = None
) -> SectionBlock:
    fields = [
        MarkdownTextObject(text=name),
        MarkdownTextObject(text=started),
        MarkdownTextObject(text=status),
    ]
    if finished:
        fields.append(MarkdownTextObject(text=finished))

    return SectionBlock(
        block_id="operation",
        fields=fields,
    )
