"""
Create Reddit objects
=====================
Defining methods to create JSON serializable objects from Reddit metadata.
"""


from urs.utils.Global import convert_time

class Objectify():
    """
    Methods for creating JSON serializable objects from Reddit metadata.
    """

    def make_comment(self, comment, include_all):
        """
        Make a comment item. 
        
        Calls previously defined public method:

            self.make_submission()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        comment: PRAW comment object
        include_all: boolean
            Boolean to determine whether the "type" field should be included

        Returns
        -------
        redditor_item: dict
            Dictionary containing comment metadata
        """

        comment_object = {
            "author": "u/" + comment.author.name \
                if hasattr(comment.author, "name") \
                else "[deleted]",
            "body": comment.body,
            "body_html": comment.body_html,
            "created_utc": convert_time(comment.created_utc),
            "distinguished": comment.distinguished,
            "edited": comment.edited \
                if comment.edited == False \
                else convert_time(comment.edited),
            "id": comment.id,
            "is_submitter": comment.is_submitter,
            "link_id": comment.link_id,
            "parent_id": comment.parent_id,
            "score": comment.score,
            "stickied": comment.stickied,
        }

        if include_all:
            comment_object["submission"] = self.make_submission(include_all, comment.submission)
            comment_object["subreddit_id"] = comment.subreddit_id
            comment_object["type"] = "comment"

            comment_object = dict(sorted(comment_object.items()))

        return comment_object

    def make_multireddit(self, multireddit):
        """
        Make a multireddit item.

        Calls a previously defined public method:

            self.make_subreddit()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        multireddit: PRAW multireddit object

        Returns
        -------
        multireddit_object: dict
            Dictionary containing multireddit metadata
        """

        multireddit_object = {
            "can_edit": multireddit.can_edit,
            "copied_from": multireddit.copied_from,
            "created_utc": convert_time(multireddit.created_utc),
            "description_html": multireddit.description_html,
            "description_md": multireddit.description_md,
            "display_name": multireddit.display_name,
            "name": multireddit.name,
            "nsfw": multireddit.over_18,
            "subreddits": [],
            "visibility": multireddit.visibility
        }

        if multireddit.subreddits:
            for subreddit in multireddit.subreddits:
                subreddit = self.make_subreddit(subreddit)
                multireddit_object["subreddits"].append(subreddit)

        return multireddit_object
    
    def make_submission(self, include_all, submission):
        """
        Make a submission object.

        Calls a previously defined public method:

            self.make_subreddit()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        include_all: boolean
            Boolean to determine whether the "type" field should be included
        submission: PRAW submission object

        Returns
        -------
        submission_object: dict
            Dictionary containing submission metadata
        """

        submission_object = {
            "author": "u/" + submission.author.name \
                if hasattr(submission.author, "name") \
                else "[deleted]",
            "created_utc": convert_time(submission.created_utc),
            "distinguished": submission.distinguished,
            "edited": submission.edited \
                if submission.edited == False \
                else convert_time(submission.edited),
            "id": submission.id,
            "is_original_content": submission.is_original_content,
            "is_self": submission.is_self,
            "link_flair_text": submission.link_flair_text,
            "locked": submission.locked,
            "name": submission.name,
            "nsfw": submission.over_18,
            "num_comments": submission.num_comments,
            "permalink": submission.permalink,
            "score": submission.score,
            "selftext": submission.selftext,
            "spoiler": submission.spoiler,
            "stickied": submission.stickied,
            "title": submission.title,
            "upvote_ratio": submission.upvote_ratio,
            "url": submission.url
        }

        if include_all:
            submission_object["subreddit"] = self.make_subreddit(submission.subreddit)
            submission_object["type"] = "submission"

            submission_object = dict(sorted(submission_object.items()))

        return submission_object

    def make_subreddit(self, subreddit):
        """
        Make a Subreddit object.

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        subreddit: PRAW Subreddit object

        Returns
        -------
        subreddit_object: dict
            Dictionary containing Subreddit metadata
        """

        return {
            "can_assign_link_flair": subreddit.can_assign_link_flair,
            "can_assign_user_flair": subreddit.can_assign_user_flair,
            "created_utc": convert_time(subreddit.created_utc),
            "description": subreddit.description,
            "description_html": subreddit.description_html,
            "display_name": subreddit.display_name,
            "id": subreddit.id,
            "name": subreddit.name,
            "nsfw": subreddit.over18,
            "public_description": subreddit.public_description,
            "spoilers_enabled": subreddit.spoilers_enabled,
            "subscribers": subreddit.subscribers,
            "user_is_banned": subreddit.user_is_banned,
            "user_is_moderator": subreddit.user_is_moderator,
            "user_is_subscriber": subreddit.user_is_subscriber
        }
