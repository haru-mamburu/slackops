from __future__ import annotations
import time

from slack_sdk.web.client import WebClient
from slack_sdk.web.slack_response import SlackResponse

from . import templates


class Message:
    def __init__(self, token: str, channel: str = ""):
        """Post ``message`` template to slack.

        Note:
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.client = WebClient(token)
        self.tmpl = templates.Message()
        self.channel = channel

    def post(
        self,
        text: str = None,
        severity: str = None,
        header: str = None,
        context: list = None,
        channel: str = None,
    ) -> None:
        """Post simple message to Slack

        Args:
            severity (str): Sets message color. Possible values: info | success | warning | error

        Note:
            - If no value is passed, the default value will be used (if available).
            - If there is no default/persistent value found - that part of the template will not be rendered.
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.client.chat_postMessage(
            channel=channel or self.channel,
            **self.tmpl.construct(text, header, context, severity),
        )


def seconds_to_dhms(seconds) -> str:
    (days, remainder) = divmod(int(seconds), 86400)
    (hours, remainder) = divmod(remainder, 3600)
    (minutes, seconds) = divmod(remainder, 60)

    return "".join(
        [
            f"{v}{k} " if v else ""
            for k, v in {"d": days, "h": hours, "m": minutes, "s": seconds}.items()
        ]
    ).strip()


class Operation:
    def __init__(
        self, token: str = None, channel: str = "", packed_operation: dict = None
    ):
        """Post ``operation`` template to slack.

        Note:
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.tmpl = templates.Operation()

        if packed_operation:
            self.init_packed(packed_operation)
        else:
            self.token = token
            self.channel = channel

        self.client = WebClient(self.token)

    def start(
        self,
        name: str,
        status: str,
        text: str = None,
        severity: str = "info",
        header: str = None,
        context: list = None,
        channel: str = None,
    ) -> SlackResponse:
        """Send message to slack about operation you're starting.

        Args:
            name (str): Name of operation. Example: Application update
            status (str): Status of operation. Example: Backup

        Note:
            - If no value is passed, the default value will be used (if available).
            - If there is no default/persistent value found - that part of the template will not be rendered.
            - You can set default value using self.default.set()
            - You can set persistent value using self.persistent.set()
        """
        self.started = time.time()

        self.tmpl.default.set(
            started=self.started, text=text, name=name, header=header, context=context
        )

        response = self.client.chat_postMessage(
            channel=channel or self.channel,
            **self.tmpl.construct(status=status, severity=severity),
        )

        self._parent_ts = response["message"]["ts"]
        self._channel_id = response["channel"]
        self._post_to_parent_thread(status)

        return response

    def update(
        self,
        status: str,
        severity: str = "info",
    ):
        """Update current status of the operation"""

        self.client.chat_update(
            channel=self._channel_id,
            ts=self._parent_ts,
            **self.tmpl.construct(severity=severity, status=status),
        )

        self._post_to_parent_thread(status)

    def finish(self, status: str, severity: str = "success"):
        finished = time.time()

        self.client.chat_update(
            channel=self._channel_id,
            ts=self._parent_ts,
            **self.tmpl.construct(status=status, finished=finished, severity=severity),
        )

        self._post_to_parent_thread(
            f"The process took `{seconds_to_dhms(finished - self.started)}`"
        )

    def _post_to_parent_thread(self, text) -> SlackResponse:
        return self.client.chat_postMessage(
            text=f"`<!date^{int(time.time())}^{{time_secs}}|:( no time>`   {text}",
            mrkdwn=True,
            channel=self._channel_id,
            thread_ts=self._parent_ts,
        )

    def pack(self):
        return {
            "default": self.tmpl.default._dict,
            "persistent": self.tmpl.persistent._dict,
            "channel": self.channel,
            "_channel_id": self._channel_id,
            "_parent_ts": self._parent_ts,
            "token": self.token,
        }

    def init_packed(self, packed_operation):
        p = packed_operation
        self.token = p["token"]
        self.tmpl.default._dict = p["default"]
        self.tmpl.persistent._dict = p["persistent"]
        self.channel = p["channel"]
        self._channel_id = p["_channel_id"]
        self._parent_ts = p["_parent_ts"]
