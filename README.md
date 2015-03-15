# RTC-Slackbot
A bot that will push to slack when RTC task items status changes.

#How to Install

1. Go to your itegrations in slack and add an Incoming WebHook. Set up the default channel if you want. The program allows for you to override where you send messages so this isn't that important. Set the name to whatever you want and same with the icon. You need to grab the webhook URL so that you can place it into your env.yaml.
2. Clone this repo to somewhere on a server. Update the env-sample.yaml with the information you want. 
3. Run `python rtc-slack.py` I currently have the program running in a infinite loop but you can change it to just run once and use a cron job if you like.
