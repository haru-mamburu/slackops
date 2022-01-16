from slack_sdk.models.attachments import BlockAttachment
from . import blocks


def attachment(
    blocks: list, color: str = None, fallback: str = None
) -> BlockAttachment:
    return BlockAttachment(blocks=filter(None, blocks), color=color, fallback=fallback)  # type: ignore


class Default:
    """Simple dict 'interface' class to show which values are possible to set'"""

    def __init__(self):
        self._dict = {}

    def set(self, **kwargs) -> None:
        """Set value.

        Args:
            text (str, optional): Defaults to None.
            severity (str, optional): Defaults to "info".
            header (str, optional): Defaults to None.
            context (list, optional): Defaults to None.
            severity_colors (dict, optional): example: {"info": "#36C5F0"}
        """
        for k, v in kwargs.items():
            if v:
                self._dict[k] = v

    def get(self, k):
        return self._dict.get(k)


class Persistent(Default):
    pass


COLORS = {
    "info": "#36C5F0",
    "success": "#2EB67D",
    "warning": "#ECB22E",
    "error": "#E01E5A",
}


# actual templates


class Template:
    values: dict

    attachments: list
    blocks: list
    text: str

    def __init__(self):
        self.persistent = Persistent()
        self.default = Default()
        self.default.set(severity_colors=COLORS)

    def apply_default_values(self, values: dict) -> dict:
        return {k: v or self.default._dict.get(k) for k, v in values.items()}

    def apply_persistent_values(self, values: dict) -> dict:
        for k, v in values.items():
            pv = self.persistent.get(k)
            if pv:
                values[k] = pv + v if v else pv
        return values

    def unpack(self) -> dict:
        return {
            "attachments": getattr(self, "attachments", None),
            "blocks": getattr(self, "blocks", None),
            "text": getattr(self, "text", None),
        }


class Message(Template):
    def __init__(self):
        super().__init__()
        self.default.set(severity="info")

    def construct(
        self,
        text: str = None,
        header: str = None,
        context: list = None,
        severity: str = None,
    ):
        values = self.apply_persistent_values(
            self.apply_default_values(
                {
                    "severity": severity,
                    "header": header,
                    "text": text,
                    "context": context,
                }
            )
        )

        fallback = values["text"] or values["header"]
        color = self.default.get("severity_colors")[values["severity"]]  # type: ignore

        self.attachments = [
            attachment(
                blocks=[
                    blocks.header(values.get("header")),
                    blocks.text(values.get("text")),
                    *blocks.context(values.get("context")),
                ],
                color=color,
                fallback=fallback,
            )
        ]

        return self.unpack()


class Operation(Template):
    def __init__(self):
        super().__init__()

        self.persistent.set(
            name="*Operation*:\n",
            status="*Status:*\n",
            started="*Started:*\n",
            finished="*Finished:*\n",
        )

        self.time_fmt = "<!date^{time}^{{date_short_pretty}} {{time_secs}}|:( no time>"

    def construct(
        self,
        name: str = None,
        status: str = None,
        text: str = None,
        header: str = None,
        context: list = None,
        started: float = None,
        finished: float = None,
        severity: str = None,
    ):
        values = self.apply_default_values(
            {
                "severity": severity,
                "header": header,
                "text": text,
                "context": context,
                "name": name,
                "status": status,
                "started": started,
                "finished": finished,
            }
        )
        if not values["finished"]:
            del values["finished"]
        else:
            values["finished"] = self.time_fmt.format(time=int(values["finished"]))

        values["started"] = self.time_fmt.format(time=int(values["started"]))

        fallback = values["status"]
        color = self.default.get("severity_colors")[severity]  # type: ignore

        values = self.apply_persistent_values(values)
        self.attachments = [
            attachment(
                blocks=[
                    blocks.header(values["header"]),
                    blocks.text(values["text"]),
                    blocks.operation(
                        name=values["name"],
                        status=values["status"],
                        started=values["started"],
                        finished=values.get("finished"),
                    ),
                    *blocks.context(values["context"]),
                ],
                color=color,
                fallback=fallback,
            )
        ]

        return self.unpack()
