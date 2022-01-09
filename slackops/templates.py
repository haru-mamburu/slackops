from .blocks import AttachmentTemplate

from datetime import datetime

# simple 'interface' classes to show what default values
# are possible to set. If you know better way do do it - pm me :)


class Default:
    def __init__(self):
        self._defaults = {}

    def set(self, **kwargs) -> None:
        """Set default value.

        Args:
            text (str, optional): Defaults to None.
            severity (str, optional): Defaults to "info".
            header (str, optional): Defaults to None.
            context (list, optional): Defaults to None.
            severity_colors (dict, optional): example: {"info": "#36C5F0"}
        """
        for k, v in kwargs.items():
            if v:
                self._defaults[k] = v

    def get(self, k):
        return self._defaults.get(k)


class Persistent(Default):
    def __init__(self):
        super().__init__()

    def set(self, **kwargs) -> None:
        """Set persistent value.

        Args:
            text (str, optional): Defaults to None.
            severity (str, optional): Defaults to "info".
            header (str, optional): Defaults to None.
            context (list, optional): Defaults to None.
        """
        super().set(**kwargs)


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

    def set_default_and_persistent_values(self, values: dict):
        for k, v in values.items():
            v = v or self.default.get(k)
            p = self.persistent.get(k)
            if p:
                v = p + v if v else p

            values[k] = v
        return values

    def unpack(self) -> dict:

        template = {}
        for k in ["attachments", "blocks", "text"]:
            v = getattr(self, k, None)
            if v:
                template[k] = v
                delattr(self, k)

        return template


class MessageTemplate(Template):
    def __init__(self):
        super().__init__()

    def construct(
        self,
        text: str = None,
        severity: str = None,
        header: str = None,
        context: list = None,
    ):
        values = locals()
        del values["self"]

        values = self.set_default_and_persistent_values(values)
        values["color"] = self.default.get(values.pop("severity"))

        self.attachments = [AttachmentTemplate.message(**values)]


class OperationTemplate(Template):
    def __init__(self):
        super().__init__()

        self.persistent.set(
            name="*Operation*:\n",
            status="*Status:*\n",
            started="*Started:*\n",
            finished="*Finished:*\n",
        )

    def construct(
        self,
        text: str = None,
        name: str = None,
        severity: str = None,
        header: str = None,
        status: str = None,
        context: list = None,
        started: datetime = None,
        finished: str = None,
    ):
        values = locals()
        del values["self"]

        values = self.set_default_and_persistent_values(values)
        severity = values.pop("severity")
        severity_colors = self.default.get("severity_colors") or {}
        values["color"] = severity_colors.get(severity)

        if values["finished"] == self.persistent.get("finished"):
            del values["finished"]

        self.attachments = [AttachmentTemplate.operation(**values)]
