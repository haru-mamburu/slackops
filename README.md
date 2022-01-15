# SlackOps
Post process information to the slack without clogging up the channel with a bunch of messages. Easyly update status, see when operation started / finished and how much time it took.

## Installation
```bash
$ pip install slackops
```
## Usage
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

Operation statuses also posted to thread.

![Thread messages](https://raw.githubusercontent.com/haru-mamburu/slackops/master/docs/images/5-thread-messages.png)