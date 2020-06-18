from urs.utils import Validation

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 20 tests.

class TestValidationValidateUserMethod():
    """
    Testing Validation class validate_user() method found on line 25 in 
    Validation.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_validate_user_valid_credentials(self):
        pass

    def test_validate_user_invalid_credentials(self):
        pass

class TestValidationCheckSubredditsMethod():
    """
    Testing Validation class _check_subreddits() method found on line 31 in
    Validation.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_check_subreddits_valid_subreddits(self):
        pass

    def test_check_subreddits_invalid_subreddits(self):
        pass

    def test_check_subreddits_valid_and_invalid_subreddits(self):
        pass

class TestValidationCheckRedditorsMethod():
    """
    Testing Validation class _check_redditors() method found on line 41 in 
    Validation.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_check_redditors_valid_redditors(self):
        pass

    def test_check_redditors_invalid_redditors(self):
        pass

    def test_check_redditors_valid_and_invalid_redditors(self):
        pass

class TestValidationCheckSubmissionsMethod():
    """
    Testing Validation class _check_submissions() method found on line 51 in
    Validation.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_check_submissions_valid_submissions(self):
        pass

    def test_check_submissions_invalid_submissions(self):
        pass

    def test_check_submissions_valid_and_invalid_submissions(self):
        pass

class TestValidationExistenceMethod():
    """
    Testing Validation class existence() method found on line 61 in Validation.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_existence_valid_subreddits(self):
        pass

    def test_existence_invalid_subreddits(self):
        pass

    def test_existence_valid_and_invalid_subreddits(self):
        pass

    def test_existence_valid_redditors(self):
        pass

    def test_existence_invalid_redditors(self):
        pass

    def test_existence_valid_and_invalid_redditors(self):
        pass

    def test_existence_valid_submissions(self):
        pass

    def test_existence_invalid_submissions(self):
        pass

    def test_existence_valid_and_invalid_submissions(self):
        pass
