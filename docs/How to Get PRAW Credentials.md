# How to Get PRAW Credentials

### Create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps). 

### Click "are you a developer? create an app... ". 

![Create an app][Create an app]

### Name your app, choose "script" for the type of app, and type "http://localhost:8080" in the redirect URI field since this is a personal use app. You can also add a description and an about URL. 

![Enter Stuff In Boxes][Enter Stuff In Boxes]

### Click "create app", then "edit" to reveal more information. 

![Click Edit][Click Edit]

### You should see a string of 14 characters on the top left corner underneath "personal use script. " That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. **Save this information as it will be used in the program in order to use the Reddit API**. 

![All Info][All Info]

### You will also have to provide your app name as well as your Reddit account username and password in the block of credentials found in `.env`.

<!-- SCREENSHOT LINKS -->
[Create an app]: https://i.imgur.com/Bf0pKGJ.png
[Enter Stuff In Boxes]: https://i.imgur.com/g0xARWA.png
[Click Edit]: https://i.imgur.com/1NOyMTN.png
[All Info]: https://i.imgur.com/VajTKJu.png
