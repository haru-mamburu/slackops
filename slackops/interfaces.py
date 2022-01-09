from __future__ import annotations
from typing import Iterable

import pytz
from datetime import datetime
import time

from slack_sdk.web.client import WebClient
from slack_sdk.web.slack_response import SlackResponse

from .templates import MessageTemplate, OperationTemplate


class Message:
    def __init__(self, token: str, channel: str = ""):
        """Post ``message`` template to slack.

        Note:
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.client = WebClient(token)
        self.tmpl = MessageTemplate()
        self.channel = channel

    def post(
        self,
        text: str = None,
        severity: str = "info",
        header: str = None,
        context: list = None,
        channel: str = "",
    ) -> None:
        """Post simple message to Slack

        Args:
            text (str, optional): Defaults to None.
            severity (str, optional): Defaults to "info".
            header (str, optional): Defaults to None.
            context (list, optional): Defaults to None.
            channel (str, optional): Defaults to "".

        Note:
            - If no value is passed, the default value will be used (if available).
            - If there is no default/persistent value found - that part of the template will not be rendered.
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.tmpl.construct(text, severity, header, context)

        channel = channel or self.channel
        self.client.chat_postMessage(
            channel=channel,
            **self.tmpl.unpack(),
        )


class Operation:
    def __init__(self, token: str, channel: str = "", timezone="Europe/Moscow"):
        """Post ``operation`` template to slack.

        Note:
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.client = WebClient(token)
        self.tmpl = OperationTemplate()
        self.channel = channel

        self.timezone = timezone
        self.time_format = "%d %b, %H:%M:%S"
        self.period_time_format = "{h}h:{m}m:{s}s"

        self.thread_time_format = "%H:%M:%S"

    @property
    def timezone(self):
        return self._str_timezone

    @timezone.setter
    def timezone(self, value: str):
        self._str_timezone = value
        self._timezone = pytz.timezone(value)

    def start(
        self,
        name: str,
        status: str,
        text: str = None,
        severity: str = "info",
        header: str = None,
        context: list = None,
        channel: str = "",
    ) -> SlackResponse:
        """Send message to slack about operation you're starting

        Args:
            name (str): Operation, that you about to start.
                Example: ``Application update``
            status (str): Current status of operation.
                Example: ``DB backup``

        Optional (will be set as default values):
            text (str, optional): Defaults to None.
            severity (str, optional): Defaults to "info".
            header (str, optional): Defaults to None.
            context (list, optional): Defaults to None.
            channel (str, optional): Defaults to "".

        Note:
            - If no value is passed, the default value will be used (if available).
            - If there is no default/persistent value found - that part of the template will not be rendered.
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.started = datetime.now(self._timezone)

        fmt_time = self.started.strftime(self.time_format)  # type: ignore

        self.tmpl.default.set(
            started=fmt_time, text=text, name=name, header=header, context=context
        )

        self.tmpl.construct(text, name, severity, header, status, context)

        channel = channel or self.channel
        r = self.client.chat_postMessage(channel=channel, **self.tmpl.unpack())

        self._parent_ts = r["message"]["ts"]
        self._channel_id = r["channel"]
        self._post_to_parent_thread(status)
        return r

    def update(
        self,
        status: str,
        severity: str = "info",
    ) -> None:
        """Update current status of the operation"""

        self.tmpl.construct(severity=severity, status=status)
        self.client.chat_update(
            channel=self._channel_id, ts=self._parent_ts, **self.tmpl.unpack()
        )

        self._post_to_parent_thread(status)

    def finish(self, status: str, severity: str = "success") -> None:
        end_time = datetime.now(self._timezone)

        finish_time = end_time.strftime(self.time_format)  # type: ignore

        self.tmpl.construct(status=status, finished=finish_time, severity=severity)
        self.client.chat_update(
            channel=self._channel_id, ts=self._parent_ts, **self.tmpl.unpack()
        )
        self._post_to_parent_thread(
            f"The process took `{self.period(end_time - self.started)}`."
        )

    def _post_to_parent_thread(self, text):
        time_fmt = f"<!date^{int(time.time())}^{{time_secs}}|Error>"

        self.client.chat_postMessage(
            text=f"`{time_fmt}`   {text}",
            mrkdwn=True,
            channel=self._channel_id,
            thread_ts=self._parent_ts,
        )

    def period(self, delta):
        """Format timedelta"""
        d = {"d": delta.days}
        d["h"], rem = divmod(delta.seconds, 3600)
        d["m"], d["s"] = divmod(rem, 60)
        return self.period_time_format.format(**d)

    def load_template_values(self, ts, channel_id) -> Iterable:
        """Load template values from parent message"""
        self._channel_id = channel_id
        self._parent_ts = ts

        response = self.client.conversations_history(
            channel=self._channel_id,
            inclusive=True,
            limit=1,
            latest=self._parent_ts,
        )
        blocks = response.data["messages"][0]["attachments"][0]["blocks"]

        for b in blocks:
            id = b["block_id"]

            if id == "context":
                context_blocks = b.get("elements")
                if context_blocks:
                    yield "context", list([cb.get("text") for cb in context_blocks])

            if id == "header":
                yield "header", b.get("text").get("text")

            if id == "text":
                yield "text", b.get("text").get("text")

            if id == "operation":
                f = b.get("fields")
                if f:
                    for i, value in enumerate(["name", "started", "status"]):
                        yield value, f[i].get("text").split("\n")[1]

    def parent(self, ts, channel_id):
        """Load template values from parent message"""
        kwargs = dict(self.load_template_values(ts, channel_id))

        started_string = kwargs["started"]
        started_dt = datetime.strptime(
            started_string, self.time_format  # type: ignore
        )  # no year in dt string, so we will use current

        dt_with_year = started_dt.replace(year=datetime.now().year)
        self.started = pytz.timezone(self.timezone).localize(dt_with_year)

        self.tmpl.persistent.set(
            text=kwargs["text"], header=kwargs["header"], context=kwargs["context"]
        )

        self.tmpl.default.set(
            name=kwargs["name"],
            started=kwargs["started"],
            status=kwargs["status"],
        )
