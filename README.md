# SlackOps
Post process information to the slack without clogging up the channel with a bunch of messages. Easyly update status, see when operation started / finished and how much time it took.

## Installation
```bash
$ pip install slackops
```
## Usage
```python
import slackops

slack = Operation(token=SLACK_BOT_TOKEN, channel=CHANNEL_NAME)

slack.start("Application update", "Backup")
```
![Screenshot](/docs/images/1-start.png)

```python
slack.update("2. Updating application")
```
![Screenshot](/docs/images/2-update.png)

```python
slack.update("3. Healthchecks")
```
![Screenshot](/docs/images/3-update.png)

```python
slack.finish("4. Application successfully updated!")
```
![Screenshot](/docs/images/4-finish.png)
![Screenshot](/docs/images/5-thread-messages.png)