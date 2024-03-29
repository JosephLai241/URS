# Two-Factor Authentication

If you choose to use 2FA with your Reddit account, enter your password followed by a colon and then your 2FA token in the `password` field on line 26. For example, if your password is `"p4ssw0rd"` and your 2FA token is `"123456"`, you will enter `"p4ssw0rd:123456"` in the `password` field.

**2FA is NOT recommended for use with this program.** This is because PRAW will raise an OAuthException after one hour, prompting you to refresh your 2FA token and re-enter your credentials. Additionally, this means your 2FA token would be stored alongside your Reddit username and password, which would defeat the purpose of enabling 2FA in the first place. See [here](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#two-factor-authentication) for more information.
