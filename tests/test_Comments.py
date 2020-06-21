from urs.utils import Comments

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 29 tests.

class TestCheckSubmissionsListPostsMethod():
    """
    Testing CheckSubmissions class list_posts() method found on line 25 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_list_submissions_valid_subreddits(self):
        pass

    def test_list_submissions_invalid_subreddits(self):
        pass

    def test_list_submissions_no_subreddits_left_to_process(self):
        pass

class TestGetCommentsInitMethod():
    """
    Testing PrintPosts class __init__() method found on line 48 in Comments.py.
    """

    def test_get_comments_init_method_titles_instance_variable(self):
        assert Comments.GetComments()._titles == ["Parent ID", "Comment ID", 
            "Author", "Date Created", "Upvotes", "Text", "Edited?", 
            "Is Submitter?", "Stickied?"]

class TestGetCommentsFixAttributesMethod():
    """
    Test GetComments class _fix_attributes() method found on line 53 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_comments_fix_attributes_author_exists(self):
        pass

    def test_get_comments_fix_attributes_author_deleted(self):
        pass

    def test_get_comments_fix_attributes_comment_was_edited(self):
        pass
    
    def test_get_comments_fix_attributes_comment_was_not_edited(self):
        pass

class TestGetCommentsAddCommentMethod():
    """
    Testing GetComments class add_comment() method found on line 65 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_comments_add_comment(self):
        pass

class TestSortCommentsRawCommentsMethod():
    """
    Testing SortComments class _raw_comments() method found on line 86 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_raw_comments(self):
        pass
    
class TestSortCommentsLevelMethods():
    """
    Testing SortComments class functions for structured export in Comments.py:
    _top_level_comment() on line 92,
    _second_level_comment() on line 98,
    _third_level_comment() on line 104.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_top_level_comment(self):
        pass

    def test_second_level_comment(self):
        pass
    
    def test_third_level_comment(self):
        pass

class TestSortCommentsStructuredCommentsMethod():
    """
    Testing SortComments class _structured_comments() method on line 115 in 
    Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_structured_coments_top_level(self):
        pass

    def test_structured_comments_second_level(self):
        pass

    def test_structured_comments_third_level(self):
        pass

class TestSortCommentsToAllMethod():
    """
    Testing SortComments class _to_all() method on line 125 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_to_all_raw_comments(self):
        pass

    def test_to_all_structured_comments(self):
        pass

class TestSortCommentsSortMethod():
    """
    Testing SortComments class sort() method on line 134 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_sort(self):
        pass

class TestGetSortInitMethod():
    """
    Testing GetSort __init__() method found on line 144 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_sort_init_method_submission_instance_variable(self):
        pass

class TestGetSortGetRawMethod():
    """
    Testing GetSort _get_raw() method found on line 152 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_raw(self):
        pass

class TestGetSortGetStructuredMethod():
    """
    Testing GetSort _get_structured() method found on line 160 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_structured(self):
        pass

class TestGetSortGetSortMethod():
    """
    Testing GetSort get_sort() method found on line 170 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_get_sort_get_raw_comments_export(self):
        pass

    def test_get_sort_get_structured_export(self):
        pass

class TestWriteDetermineExportMethod():
    """
    Test Write _determine_export() method found on line 186 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_write_determine_json(self):
        pass

    def test_write_determine_csv(self):
        pass

class TestWritePrintConfirmMethod():
    """
    Test Write _print_confirm() method found on line 193 in Comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_print_confirm_json(self):
        pass

    def test_print_confirm_csv(self):
        pass

class TestWriteWriteMethod():
    """
    Test Write write() method found on line 202 in comments.py.
    Have to find a way to test functions that access Reddit without exposing my 
    personal credentials. Passing for now.
    """

    def test_write(self):
        pass

