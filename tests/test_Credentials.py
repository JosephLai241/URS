from urs import Credentials

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 5 tests.

class TestDefaultCredentialsDictionary():
    """
    Testing the default `API` dictionary found on line 5 in Credentials.py.
    """

    def test_api_dictionary_client_id(self):
        assert Credentials.API["client_id"] == "14_CHAR_HERE"

    def test_api_dictionary_client_secret(self):
        assert Credentials.API["client_secret"] == "27_CHAR_HERE"

    def test_api_dictionary_user_agent(self):
        assert Credentials.API["user_agent"] == "APP_NAME_HERE"

    def test_api_dictionary_username(self):
        assert Credentials.API["username"] == "REDDIT_USERNAME_HERE"

    def test_api_dictionary_password(self):
        assert Credentials.API["password"] == "REDDIT_PASSWORD_HERE"
