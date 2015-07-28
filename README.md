# IDS-Slackbot
A python application that serves as a go-between of the IDS(IBM Bluemix Devops Services) Track and Plan dashboards and slack.

## Usage

```
usage: /ids [-h] [-t {task,defect,story,epic}] [-s {new,in-progress}]
           [-p {high,medium,low}] [-n N] [-a]
           first_name last_name

Application that queries Track and Plan dashboards and sends results to slack.

positional arguments:
 first_name
 last_name

optional arguments:
 -h, --help            show this help message and exit
 -t {task,defect,story,epic}, --type {task,defect,story,epic}
                       Filter for a specific type of work item
 -s {new,in-progress}, --state {new,in-progress}
                       Filter for work items in a specific state
 -p {high,medium,low}, --priority {high,medium,low}
                       Filter for work items with a specific priority
 -n N                  Number of work items to retrieve. Default is 5.
 -a, --all             Returns all work items
```

----

## Installation Instructions

#### Setting up slack

You will need to add two slack integrations. One slash command and one incoming webhook.

Point the slash command to the ip of your instance running docker and use port 8091. Copy down the token provided by the slash command and copy the incoming webhook url from it's integration.

#### Setting the environment variables

You will need to add these values during the setup in the next section. This is here for reference

| *Variable*   | *Explanation* |
|------------|----------------------------------------------------|
| *user* | Your IBM Single Sign on Username   |
| *pass* | Your IBM Single Sign on Password   |
| *server* | The Jazz server your team is using. Ex. `ccm08`. Look at the URL when on your dashboard.   |
| *slack_url* | The url of your incoming web hook   |

#### Deploy with Docker

```
# Get the source code
git clone https://github.com/jroyal/IDS-Slackbot.git
cd IDS-Slackbot

# Update the env file with your info
vim env.list

# Deploy
docker build -t jroyal/ids-slack:latest .
docker run -d --env-file env.list -p 8091:5000 jroyal/ids-slack
```



-----

### Suggestions or bugs?

Go and make an issue and tag it as a bug or enhancement. I will try to get an update out for bugs as soon as I can, and I'll do my best to add enhancements. Better yet, if you have a fix or new feature to add create a pull request for us. :)


