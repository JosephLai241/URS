from urs.utils import Global, Redditor

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 47 tests.

class TestCheckRedditorsListUser():
    """
    Testing CheckRedditors list_users() method found on line 27 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_list_redditors_valid_redditors(self):
        pass

    def test_list_redditors_invalid_redditors(self):
        pass

    def test_list_redditors_no_redditors_left_to_process(self):
        pass

class TestProcessInteractionsInitMethod():
    """
    Testing ProcessInteractions __init__() method found on line 60 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_process_interactions_init_method_overview_instance_variable(self):
        pass

    def test_process_interactions_init_method_comments_instance_variable(self):
        pass

    def test_process_interactions_init_method_controversial_instance_variable(self):
        pass

    def test_process_interactions_init_method_downvoted_instance_variable(self):
        pass

    def test_process_interactions_init_method_gilded_instance_variable(self):
        pass
    
    def test_process_interactions_init_method_gildings_instance_variable(self):
        pass

    def test_process_interactions_init_method_hidden_instance_variable(self):
        pass

    def test_process_interactions_init_method_hot_instance_variable(self):
        pass

    def test_process_interactions_init_method_new_instance_variable(self):
        pass

    def test_process_interactions_init_method_saved_instance_variable(self):
        pass

    def test_process_interactions_init_method_submissions_instance_variable(self):
        pass

    def test_process_interactions_init_method_top_instance_variable(self):
        pass

    def test_process_interactions_init_method_upvoted_instance_variable(self):
        pass

    def test_process_interactions_init_method_comment_titles_instance_variable(self):
        # limit = 1
        # overview = {}
        # user = None
        
        # assert Redditor.ProcessInteractions(limit, overview, user)._comment_titles == \
        #     ["Date Created", "Score", "Text", "Parent ID", "Link ID", "Edited?", 
        #     "Stickied?", "Replying to", "In Subreddit"]

        pass

    def test_process_interactions_init_method_submission_titles_instance_variable(self):
        # limit = 1
        # overview = {}
        # user = None
        
        # assert Redditor.ProcessInteractions(limit, overview, user)._submission_titles == \
        #     ["Title", "Date Created", "Upvotes", "Upvote Ratio","ID", "NSFW?", 
        #     "In Subreddit", "Body"]

        pass

    def test_process_interactions_init_method_s_types_instance_variable(self):
        # limit = 1
        # overview = {}
        # user = None
        
        # assert Redditor.ProcessInteractions(limit, overview, user)._s_types == \
        #     ["Submissions", "Comments", "Mutts", "Access"]

        pass

    def test_process_interactions_init_method_mutts_instance_variable(self):
        pass

    def test_process_interactions_init_method_mutt_names_instance_variable(self):
        # limit = 1
        # overview = {}
        # user = None
        
        # assert Redditor.ProcessInteractions(limit, overview, user)._mutt_names == \
        #     ["Controversial", "Gilded", "Hot", "New", "Top"]

        pass

    def test_process_interactions_init_method_access_instance_variable(self):
        pass

    def test_process_interactions_init_method_access_names_instance_variable(self):
        # limit = 1
        # overview = {}
        # user = None
        
        # assert Redditor.ProcessInteractions(limit, overview, user)._access_names == \
        #     ["Downvoted", "Gildings", "Hidden", "Saved", "Upvoted"]

        pass

class TestProcessInteractionsMakeZipDictMethod():
    """
    Testing ProcessInteractions _make_zip_dict() method found on line 92 in 
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_make_zip_dict(self):
        # limit = 1
        # overview = {}
        # user = None

        # titles = ["this", "is", "a", "test"]
        # items = ["the", "second", "line", "here"]

        # assert Redditor.ProcessInteractions(limit, overview, user). \
        #     _make_zip_dict(titles, items) == {
        #         "this": "the", 
        #         "is": "second",
        #         "a": "line",
        #         "test": "here"
        #         }

        pass

class TestProcessInteractionsSubmissionAndCommentsListMethods():
    """
    Testing ProcessInteractions class functions for making comments and submission
    lists in Redditor.py:
    _make_submission_list() on line 96,
    _make_comment_list() on line 103
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_make_submission_list(self):
        pass

    def test_make_comments_list(self):
        pass

class TestProcessInteractionsDetermineAppendMethod():
    """
    Testing ProcessInteractions class _determine_append() method found on line
    113 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_determine_append_submissions_switch(self):
        # cat = None
        # redditor_list = []
        # s_type = 

        pass

    def test_determine_append_comments_switch(self):
        pass

    def test_determine_append_mutts_switch(self):
        pass

    def test_determine_append_access_switch(self):
        pass

class TestProcessInteractionsExtractMethod():
    """
    Testing ProcessInteractions class _extract() method found on line 126 in 
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_extract_submission_list(self):
        pass

    def test_extract_comment_list(self):
        pass

class TestProcessInteractionsSortSubmissionsMethod():
    """
    Testing ProcessInteractions class sort_submissions() method found on line 135
    in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_sort_submissions(self):
        pass

class TestProcessInteractionsSortCommentsMethod():
    """
    Testing ProcessInteractions class sort_comments() method found on line 139 in
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_sort_comments(self):
        pass

class TestProcessInteractionsSortMuttsMethod():
    """
    Testing ProcessInteractions class sort_mutts() method found on line 145 in 
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_sort_mutts(self):
        pass

class TestProcessInteractionsSortAccessMethod():
    """
    Testing ProcessInteractions class sort_access() method found on line 152 in 
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_sort_access_allowed(self):
        pass

    def test_sort_access_forbidden(self):
        pass

class TestGetInteractionsInitMethod():
    """
    Testing GetInteractions class __init__() method found on line 170 in Redditor.py.
    """

    def test_get_interactions_init_method_titles_instance_variable(self):
        assert Redditor.GetInteractions()._titles == \
            ["Name", "Fullname", "ID", "Date Created", "Comment Karma", 
            "Link Karma", "Is Employee?", "Is Friend?", "Is Mod?", "Is Gold?", 
            "Submissions", "Comments", "Hot", "New", "Controversial", "Top", 
            "Upvoted (may be forbidden)", "Downvoted (may be forbidden)", "Gilded", 
            "Gildings (may be forbidden)", "Hidden (may be forbidden)", 
            "Saved (may be forbidden)"]

class TestGetInteractionsMakeUserProfileMethod():
    """
    Testing GetInteractions class _make_user_profile() method found on line 179
    in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_make_user_profile(self):
        # test_overview = {
        #     'Name': [], 
        #     'Fullname': [], 
        #     'ID': [], 
        #     'Date Created': [], 
        #     'Comment Karma': [], 
        #     'Link Karma': [], 
        #     'Is Employee?': [], 
        #     'Is Friend?': [], 
        #     'Is Mod?': [], 
        #     'Is Gold?': [], 
        #     'Submissions': [], 
        #     'Comments': [], 
        #     'Hot': [], 
        #     'New': [], 
        #     'Controversial': [], 
        #     'Top': [], 
        #     'Upvoted (may be forbidden)': [], 
        #     'Downvoted (may be forbidden)': [], 
        #     'Gilded': [], 
        #     'Gildings (may be forbidden)': [], 
        #     'Hidden (may be forbidden)': [], 
        #     'Saved (may be forbidden)': []
        #     }

        # overview, user = \
        #     Redditor.GetInteractions()._make_user_profile(limit, reddit, user)

        # assert overview == test_overview

        pass

class TestGetInteractionsGetUserInfoMethod():
    """
    Testing GetInteractions class _get_user_info() method found on line 191 in 
    Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_user_info(self):
        pass

class TestGetInteractionsGetUserInteractionsMethod():
    """
    Testing GetInteractions class _get_user_interactions() method found on line 
    201 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_user_interactions(self):
        pass

class TestGetInteractionsGetMethod():
    """
    Testing GetInteractions class get() method found on line 209 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get(self):
        pass

class TestWriteInitMethod():
    """
    Testing Write class __init__() method found on line 222 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_write_init_method_eo_instance_variable(self):
        assert Redditor.Write()._eo == Global.eo

class TestWriteDetermineExportMethod():
    """
    Testing Write class _determine_export() method found on line 226 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_determine_export_csv(self):
        pass

    def test_determine_export_json(self):
        pass

class TestWritePrintConfirmMethod():
    """
    Testing Write class _print_confirm() method found on line 231 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_print_confirm(self):
        pass

class TestWriteWriteMethod():
    """
    Testing Write class write() method found on line 238 in Redditor.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_write(self):
        pass
