from __future__ import annotations
from slack_sdk.models.attachments import BlockAttachment
from slack_sdk.models.blocks.blocks import (
    SectionBlock,
    ContextBlock,
    HeaderBlock,
    Block,
    DividerBlock,
)
from slack_sdk.models.blocks.basic_components import MarkdownTextObject


class Message:
    def __init__(self, text, header="", context: list = None):
        self.text = text
        self.header = header
        self.context = context


class Operation:
    def __init__(self, name: str, status: str, started: str, finished: str | None = ""):
        self.name = name
        self.status = status
        self.started = started
        self.finished = finished

    def __bool__(self):
        return all([self.name, self.status, self.started])


class BlockTemplate:
    @staticmethod
    def header(
        text: str | None = "", block_id: str | None = "header"
    ) -> HeaderBlock | None:
        if text:
            return HeaderBlock(text=text, block_id=block_id)

    @staticmethod
    def text(text: str = None, block_id: str | None = "text") -> SectionBlock | None:
        if text:
            return SectionBlock(block_id=block_id, text=MarkdownTextObject(text=text))

    @staticmethod
    def operation(
        operation: Operation, block_id: str | None = "operation"
    ) -> SectionBlock | None:
        if operation:
            fields = [
                MarkdownTextObject(text=operation.name),
                MarkdownTextObject(text=operation.started),
                MarkdownTextObject(text=operation.status),
            ]
            if operation.finished:
                fields.append(MarkdownTextObject(text=operation.finished))

            return SectionBlock(
                block_id=block_id,
                fields=fields,
            )

    @staticmethod
    def context(
        context: list = None, block_id: str | None = "context"
    ) -> ContextBlock | None:
        if context:
            return ContextBlock(
                block_id=block_id,
                elements=[MarkdownTextObject(text=element) for element in context],
            )


class BlockComposition:
    @staticmethod
    def context(context: list = None) -> list[DividerBlock | ContextBlock | None]:
        if context:
            context = [
                DividerBlock(),
                BlockTemplate.context(context),
            ]
        return context or []

    @staticmethod
    def message(message: Message) -> list[Block | None]:
        blocks = [
            BlockTemplate.header(message.header),
            BlockTemplate.text(message.text),
            *BlockComposition.context(message.context),
        ]
        return blocks

    @staticmethod
    def operation(operation: Operation, message: Message) -> list[Block | None]:
        blocks = [
            BlockTemplate.header(message.header),
            BlockTemplate.text(message.text),
            BlockTemplate.operation(operation),
            *BlockComposition.context(message.context),
        ]
        return blocks


class AttachmentTemplate:
    @staticmethod
    def attachment(
        blocks: list, color: str = None, fallback: str = None
    ) -> BlockAttachment:
        return BlockAttachment(blocks=filter(None, blocks), color=color, fallback=fallback)  # type: ignore

    @staticmethod
    def message(
        text: str = None,
        color: str = None,
        header: str = None,
        context: list = None,
    ) -> BlockAttachment:
        blocks = BlockComposition.message(Message(text, header, context))
        fallback = text or header
        return AttachmentTemplate.attachment(
            blocks=blocks, color=color, fallback=fallback
        )

    @staticmethod
    def operation(
        name: str = "",
        status: str = "",
        started: str = "",
        header: str = None,
        text: str = None,
        context: list = None,
        color: str = None,
        finished: str = None,
    ) -> BlockAttachment:
        blocks = BlockComposition.operation(
            Operation(name, status, started, finished), Message(text, header, context)
        )
        fallback = status or text or header

        return AttachmentTemplate.attachment(
            blocks=blocks, color=color, fallback=fallback
        )
