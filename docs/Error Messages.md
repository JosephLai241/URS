# Error Messages

This document will briefly go over all the potential error messages you might run into while using URS. 

I will also go over rate limit information near the bottom of this document.

       __   
     /'__`\ 
    /\  __/ 
    \ \____\
     \/____/... Please recheck args or refer to help for usage examples.

This message appears if you have entered invalid arguments. You can use the `-h` or `--help` flag to see the help message.

     _____   
    /\ '__`\ 
    \ \ \L\ \
     \ \ ,__/... Please recheck API credentials or your internet connection.
      \ \ \/ 
       \ \_\ 
        \/_/

This message is displayed if you enter invalid API credentials or if you are not connected to the internet. Recheck `Credentials.py` to make sure the `API` dictionary's values are correct.

     __        
    /\ \       
    \ \ \      
     \ \ \  __ 
      \ \ \L\ \
       \ \____/
        \/___/... You have reached your rate limit.

    Please try again when your rate limit is reset: [DATE]

PRAW has rate limits. Rate limit information is printed in the small table underneath the login message every time you run URS.

From my research, it seems like rate limits are proportional to how much karma your account has: the more karma, the higher the rate limit. This has been implemented to mitigate spammers and bots that utilize PRAW.