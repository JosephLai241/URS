from urs.utils import Global, Tools

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 8 tests.

class TestRunInitMethod():
    """
    Testing Run class __init__() method found on line 18 in Tools.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_run_init_method_reddit_instance_variable(self):
        pass

    def test_run_init_method_args_and_parser_instance_variables(self):
        pass

    def test_run_init_method_s_t_instance_variable(self):
        # assert Tools.Run(reddit)._s_t == Global.s_t

        pass

class TestRunLoginAndArgsMethod():
    """
    Testing Run class _login_and_args() method found on line 25 in Tools.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    Do I need this test? It would also be tested in the class above...
    """

    def test_login_and_args(self):
        pass

class TestRunRunUrsMethod():
    """
    Testing Run class run_urs() method found on line 35 in Tools.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_run_urs_run_subreddit(self):
        pass

    def test_run_urs_run_redditor(self):
        pass

    def test_run_urs_run_comments(self):
        pass

    def test_run_urs_run_basic(self):
        pass
