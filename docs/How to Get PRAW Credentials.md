# How to Get PRAW Credentials

### Create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps). 

### Click "are you a developer? create an app... ". 

![Create an app](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/Reddit%20API/api_1.png)

### Name your app, choose "script" for the type of app, and type "http://localhost:8080" in the redirect URI field since this is a personal use app. You can also add a description and an about URL. 

![Enter Stuff In Boxes](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/Reddit%20API/api_2.png)

### Click "create app", then "edit" to reveal more information. 

![Click Edit](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/Reddit%20API/api_3.png)

### You should see a string of 14 characters on the top left corner underneath "personal use script. " That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. **Save this information as it will be used in the program in order to use the Reddit API**. 

![All Info](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/Reddit%20API/api_4.png)

### You will also have to provide your app name, Reddit account username and password in the block of credentials found in `Credentials.py`.