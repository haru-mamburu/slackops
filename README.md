# SlackOps
Post process information to the slack without clogging up the channel with a bunch of messages. Easyly update status, see when operation started / finished and how much time it took.

## Installation
```bash
$ pip install slackops
```
## Table of contents
* [Basic usage](#basic-usage)
* [Simple message](#basic-usage-of-the-web-client)
* [Formatting. Default and persistent values](#basic-usage-of-the-web-client)
* [AWS Lambda]()

## Basic usage
```python
import slackops

slack = slackops.Operation(token=SLACK_BOT_TOKEN, channel=CHANNEL_NAME)

slack.start("Application update", "Backup")
```

![1. Start](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/1-start.png)

```python
slack.update("2. Updating application")
```
![2. Updating application"](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/2-update.png)

```python
slack.update("3. Healthchecks")
```
![3. Healthchecks](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/3-update.png)

```python
slack.finish("4. Application successfully updated!")
```
![4. Application successfully updated!](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/4-finish.png)

Operation statuses also posted to thread:

![Thread messages](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/5-thread-messages.png)

## Simple message
Note: any formatting you see in 'Message' template (header, text, context), can also be used with 'Operation' template you seen before.

```python
slack = slackops.Message(token=SLACK_BOT_TOKEN, channel=CHANNEL_NAME)

slack.post(
    text="Example message",
    severity="error", # info | success | warning | error
    header="Header",
    context=["from ip: 192.162.1.1"],
)
```

![message](/docs/images/message.png)


## Formatting. Default and persistent values
You can set default values:
```python
slack.tmpl.default.set(context=["default context - from ip: 192.162.1.1"])
slack.tmpl.default.set(severity="success")

slack.post("If no value is passed, the default value will be used (if available).")
```

![default values](/docs/images/default_values.png)

And persistent values:
```python
slack.tmpl.persistent.set(header="API event: ")
slack.tmpl.persistent.set(text="*Details:*\n")

slack.post("username: haru\n ", header="new user!")
```

![persistent values](/docs/images/persistent_values.png)

## AWS Lambda
In progress...
