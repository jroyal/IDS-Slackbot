# RTC-Slackbot
A python application that serves as a go-between of the IDS(IBM Bluemix Devops Services) Track and Plan dashboards and slack.

## Current options that are allowed

| *Command*   | *Description* |
|------------|-----------------|
| `/workitem` | Get information on a specific work item |
| `/user` | Get a users open work items | 
| `/backlog` | Get a teams backlog | 


### How do I add an option?

There are a couple of simple steps you can follow to add in new functionality to RTC-Slackbot. I tried to make it easy to add in new options as necessary. I use flask in rtc-slack to create simple api endpoints and a package that holds the extensions. So to add new things do...

1. Create a new set of functionality in its own module. Place it inside of the extensions directory.
2. In rtc-slack.py add a new api endpoint block. It should be fairly simple after looking at the code. You can copy one of the existing ones and change what you need to as necessary. You can use `user_lookup()` as an example.
3. Preferabbly update the readme with some info on our new function.
4. Create a new pull request.

--
#### What does it look like?

![`/rtc 43746`](images/single-workitem.PNG "`/rtc 43746`")
![`/rtc-user James Royal`](images/user-workitems.PNG "`/rtc-user James Royal`")

## Well how do I install it?

Click the button below to fork into IBM DevOps Services and deploy your own copy of this application on Bluemix. Note the app will not yet work; you need to set the environment variables in bluemix and set up the slash commands in slack.

[![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/jroyal/RTC-Slackbot.git)

#### Setting up the slash commands

Go to to your slack settings where you can add integrations, and add a new slash command. If you want the full functionality of all three things you will need a slash command for each of them. Add your new Bluemix url that you got from your deploy to the URL field and add the appropriate ending for it. So for example I have a `/rtc-workitem [id]` that uses <bluemix-url>/workitem. I have something similar for the other two. Copy down the token you get from your slash command because you will need it in the next step. 

#### Setting the environment variables

Go to the [Bluemix Dashboard](https://console.ng.bluemix.net/?ace_base=true). Click on the tile that represents your new application. In the left side bar, click on `environment variables` and then in the center of the screen `USER_DEFINED`. Set the following variables.

| *Variable*   | *Explanation* |
|------------|----------------------------------------------------|
| *JAZZ_URL* | The first part of the url of your track and plan. Ex: https://hub.jazz.net/ccm08   |
| *JAZZ_USERNAME* | Your IBM Single Sign on Username   |
| *JAZZ_PASSWORD* | Your IBM Single Sign on Password   |
| *SLACK_ERROR_URL* | *Optional* The url to a incoming webhook used to post error messages   |
| *SLACK_ERROR_CHANNEL* | *Optional* The channel to post the error messages too   |
| *WORKITEM_TOKEN* | The token generated by your slack slash command   |
| *BACKLOG_TOKEN* | The token generated by your slack slash command   |
| *USER_TOKEN* | The token generated by your slack slash command   |

#### Optional Error Updates (Not currently functional. Adding it back in as time permits.)

I added the ability for a user or channel to be notified if something would have caused a server error. This was essentially so I could see if someone tried a request that failed for a reason that I didn't expect. If you would like to get this functionality create a new incoming webhook and set the two optional env variables listed in the table above.


![error](images/admin_error.PNG "error")


#### Can I install it locally?

Yes you can. The only thing you will need to do is fill out the env-sample.yaml and change the name to env.yaml. That should allow you to run the code locally. You can then send REST calls to http://localhost:5000 that spoof the /rtc calls. The payload should look something like this

![payload](images/spoof-payload.PNG "payload")

-----

### Suggestions or bugs?

Go and make an issue and tag it as a bug or enhancement. I will try to get an update out for bugs as soon as I can, and I'll do my best to add enhancements. Better yet, if you have a fix or new feature create a pull request with your it! :)


