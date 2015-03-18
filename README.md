# RTC-Slackbot
A python application that serves as a go-between of the IDS(IBM Bluemix Devops Services) Track and Plan dashboards and slack.

## Current requests that are allowed
* `/rtc [work item id]` -- Returns a link to the workitem, id, summary, and basic description.
* `/rtc [user name]` -- Returns all work items that the user owns that are in an open state.

## Well how do I install it?

Click the button below to fork into IBM DevOps Services and deploy your own copy of this application on Bluemix. Note the app will not yet work; you need to set the environment variables in bluemix and set up the slash command in slack.

[![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/jroyal/RTC-Slackbot.git)

#### Setting up the slash command

Go to to your slack settings where you can add integrations, and add a new slash command. Add your new Bluemix url that you got from your deploy to the URL field. Set up the command to /rtc or whatever else you might want. Copy down your token because you will need it in the next step.

#### Setting the environment variables

Go to the [Bluemix Dashboard](https://console.ng.bluemix.net/?ace_base=true). Click on the tile that represents your new application. In the left side bar, click on `environment variables` and then in the center of the screen `USER_DEFINED`. Set the following variables.
* JAZZ_URL
* JAZZ_USERNAME
* JAZZ_PASSWORD
* SLACK_TOKEN

