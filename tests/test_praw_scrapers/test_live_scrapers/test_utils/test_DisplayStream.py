"""
Testing `DisplayStream.py`.
"""


from prettytable import PrettyTable

from urs.praw_scrapers.live_scrapers.utils import DisplayStream


class CreatePrettyTable:
    """
    Create a PrettyTable for testing.
    """

    @staticmethod
    def create():
        pretty_stream = PrettyTable()
        pretty_stream.field_names = ["Attribute", "Data"]

        return pretty_stream


class TestDisplayStreamPopulateTableMethod:
    """
    Testing DisplayStream class _populate_table() method.
    """

    def test_populate_table_method_with_comment_object(self):
        test_include_fields = [
            "author",
            "body",
            "created_utc",
            "distinguished",
            "edited",
            "id",
            "is_submitter",
            "link_id",
            "parent_id",
            "score",
            "stickied",
        ]

        test_object = {
            "author": "u/Flatworm1",
            "body": "They all went to bed hours ago.",
            "body_html": '<div class="md"><p>They all went to bed hours ago.</p>\n</div>',
            "created_utc": "05-23-2021 20:47:55",
            "distinguished": None,
            "edited": False,
            "id": "gz811x5",
            "is_submitter": False,
            "link_id": "t3_njlm8y",
            "parent_id": "t3_njlm8y",
            "score": 1,
            "stickied": False,
            "submission": {
                "author": "u/Lanre-Haliax",
                "created_utc": "05-23-2021 20:46:39",
                "distinguished": None,
                "edited": False,
                "id": "njlm8y",
                "is_original_content": False,
                "is_self": True,
                "link_flair_text": None,
                "locked": False,
                "name": "t3_njlm8y",
                "nsfw": False,
                "num_comments": 2,
                "permalink": "/r/AskReddit/comments/njlm8y/people_who_where_at_woodstock_in_1969_how_was_it/",
                "score": 4,
                "selftext": "",
                "spoiler": False,
                "stickied": False,
                "subreddit": {
                    "can_assign_link_flair": False,
                    "can_assign_user_flair": False,
                    "created_utc": "01-24-2008 22:52:15",
                    "description": "###### [ [ SERIOUS ] ](http://www.reddit.com/r/askreddit/submit?selftext=true&title=%5BSerious%5D)\n\n\n##### [Rules](https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules):\n1. You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-)\n\n2. Any post asking for advice should be generic and not specific to your situation alone. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-)\n\n3. Askreddit is for open-ended discussion questions. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-)\n\n4. Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-)\n\n5. Askreddit is not your soapbox, personal army, or advertising platform. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-)\n\n6. [Serious] tagged posts are off-limits to jokes or irrelevant replies. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n7. Soliciting money, goods, services, or favours is not allowed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-)\n\n8. Mods reserve the right to remove content or restrict users' posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-)\n\n9. Comment replies consisting solely of images will be removed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-)\n\n##### If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit), we're happy to help.\n\n---\n\n#### Tags to use:\n\n> ## [[Serious]](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n### Use a **[Serious]** post tag to designate your post as a serious, on-topic-only thread.\n\n-\n\n#### Filter posts by subject:\n\n[Mod posts](http://ud.reddit.com/r/AskReddit/#ud)\n[Serious posts](https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&sort=new&restrict_sr=on&t=all)\n[Megathread](http://bu.reddit.com/r/AskReddit/#bu)\n[Breaking news](http://nr.reddit.com/r/AskReddit/#nr)\n[Unfilter](/r/AskReddit)\n\n\n-\n\n### Please use spoiler tags to hide spoilers. `>!insert spoiler here!<`\n\n-\n\n#### Other subreddits you might like:\nsome|header\n:---|:---\n[Ask Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others)|[Self & Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others)\n[Find a subreddit](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit)|[Learn something](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something)\n[Meta Subs](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta)|[What is this ___](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______)\n[AskReddit Offshoots](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots)|[Offers & Assistance](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance)\n\n\n-\n\n### Ever read the reddiquette? [Take a peek!](/wiki/reddiquette)\n\n[](#/RES_SR_Config/NightModeCompatible)",
                    "description_html": '<!-- SC_OFF --><div class="md"><h6><a href="http://www.reddit.com/r/askreddit/submit?selftext=true&amp;title=%5BSerious%5D"> [ SERIOUS ] </a></h6>\n\n<h5><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules">Rules</a>:</h5>\n\n<ol>\n<li><p>You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-">more &gt;&gt;</a></p></li>\n<li><p>Any post asking for advice should be generic and not specific to your situation alone. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is for open-ended discussion questions. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-">more &gt;&gt;</a></p></li>\n<li><p>Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is not your soapbox, personal army, or advertising platform. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-">more &gt;&gt;</a></p></li>\n<li><p>[Serious] tagged posts are off-limits to jokes or irrelevant replies. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">more &gt;&gt;</a></p></li>\n<li><p>Soliciting money, goods, services, or favours is not allowed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-">more &gt;&gt;</a></p></li>\n<li><p>Mods reserve the right to remove content or restrict users&#39; posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-">more &gt;&gt;</a></p></li>\n<li><p>Comment replies consisting solely of images will be removed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-">more &gt;&gt;</a></p></li>\n</ol>\n\n<h5>If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to <a href="https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit">contact the mods</a>, we&#39;re happy to help.</h5>\n\n<hr/>\n\n<h4>Tags to use:</h4>\n\n<blockquote>\n<h2><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">[Serious]</a></h2>\n</blockquote>\n\n<h3>Use a <strong>[Serious]</strong> post tag to designate your post as a serious, on-topic-only thread.</h3>\n\n<h2></h2>\n\n<h4>Filter posts by subject:</h4>\n\n<p><a href="http://ud.reddit.com/r/AskReddit/#ud">Mod posts</a>\n<a href="https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&amp;sort=new&amp;restrict_sr=on&amp;t=all">Serious posts</a>\n<a href="http://bu.reddit.com/r/AskReddit/#bu">Megathread</a>\n<a href="http://nr.reddit.com/r/AskReddit/#nr">Breaking news</a>\n<a href="/r/AskReddit">Unfilter</a></p>\n\n<h2></h2>\n\n<h3>Please use spoiler tags to hide spoilers. <code>&gt;!insert spoiler here!&lt;</code></h3>\n\n<h2></h2>\n\n<h4>Other subreddits you might like:</h4>\n\n<table><thead>\n<tr>\n<th align="left">some</th>\n<th align="left">header</th>\n</tr>\n</thead><tbody>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others">Ask Others</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others">Self &amp; Others</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit">Find a subreddit</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something">Learn something</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta">Meta Subs</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______">What is this ___</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots">AskReddit Offshoots</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance">Offers &amp; Assistance</a></td>\n</tr>\n</tbody></table>\n\n<h2></h2>\n\n<h3>Ever read the reddiquette? <a href="/wiki/reddiquette">Take a peek!</a></h3>\n\n<p><a href="#/RES_SR_Config/NightModeCompatible"></a></p>\n</div><!-- SC_ON -->',
                    "display_name": "AskReddit",
                    "id": "2qh1i",
                    "name": "t5_2qh1i",
                    "nsfw": False,
                    "public_description": "r/AskReddit is the place to ask and answer thought-provoking questions.",
                    "spoilers_enabled": True,
                    "subscribers": 32355402,
                    "user_is_banned": False,
                    "user_is_moderator": False,
                    "user_is_subscriber": False,
                },
                "title": "People who where at Woodstock in 1969, how was it?",
                "type": "submission",
                "upvote_ratio": 1.0,
                "url": "https://www.reddit.com/r/AskReddit/comments/njlm8y/people_who_where_at_woodstock_in_1969_how_was_it/",
            },
            "subreddit_id": "t5_2qh1i",
            "type": "comment",
        }

        test_prefix = ""
        test_pretty_stream = CreatePrettyTable.create()

        try:
            DisplayStream.DisplayStream._populate_table(
                test_include_fields, test_object, test_prefix, test_pretty_stream
            )
            assert True
        except Exception as e:
            print(
                "An exception has occurred when attempting to populate PrettyStream:", e
            )
            assert False

    def test_populate_table_method_with_submission_object(self):
        test_include_fields = [
            "author",
            "created_utc",
            "distinguished",
            "edited",
            "id",
            "is_original_content",
            "is_self",
            "link_flair_text",
            "nsfw",
            "score",
            "selftext",
            "spoiler",
            "stickied",
            "title",
            "url",
        ]

        test_object = {
            "author": "u/NuclearWinterGames",
            "created_utc": "05-24-2021 20:36:44",
            "distinguished": None,
            "edited": False,
            "id": "nkcrtr",
            "is_original_content": False,
            "is_self": True,
            "link_flair_text": None,
            "locked": False,
            "name": "t3_nkcrtr",
            "nsfw": False,
            "num_comments": 0,
            "permalink": "/r/AskReddit/comments/nkcrtr/which_song_defines_your_childhood/",
            "score": 1,
            "selftext": "",
            "spoiler": False,
            "stickied": False,
            "subreddit": {
                "can_assign_link_flair": False,
                "can_assign_user_flair": False,
                "created_utc": "01-24-2008 22:52:15",
                "description": "###### [ [ SERIOUS ] ](http://www.reddit.com/r/askreddit/submit?selftext=true&title=%5BSerious%5D)\n\n\n##### [Rules](https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules):\n1. You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-)\n\n2. Any post asking for advice should be generic and not specific to your situation alone. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-)\n\n3. Askreddit is for open-ended discussion questions. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-)\n\n4. Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-)\n\n5. Askreddit is not your soapbox, personal army, or advertising platform. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-)\n\n6. [Serious] tagged posts are off-limits to jokes or irrelevant replies. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n7. Soliciting money, goods, services, or favours is not allowed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-)\n\n8. Mods reserve the right to remove content or restrict users' posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-)\n\n9. Comment replies consisting solely of images will be removed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-)\n\n##### If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit), we're happy to help.\n\n---\n\n#### Tags to use:\n\n> ## [[Serious]](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n### Use a **[Serious]** post tag to designate your post as a serious, on-topic-only thread.\n\n-\n\n#### Filter posts by subject:\n\n[Mod posts](http://ud.reddit.com/r/AskReddit/#ud)\n[Serious posts](https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&sort=new&restrict_sr=on&t=all)\n[Megathread](http://bu.reddit.com/r/AskReddit/#bu)\n[Breaking news](http://nr.reddit.com/r/AskReddit/#nr)\n[Unfilter](/r/AskReddit)\n\n\n-\n\n### Please use spoiler tags to hide spoilers. `>!insert spoiler here!<`\n\n-\n\n#### Other subreddits you might like:\nsome|header\n:---|:---\n[Ask Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others)|[Self & Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others)\n[Find a subreddit](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit)|[Learn something](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something)\n[Meta Subs](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta)|[What is this ___](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______)\n[AskReddit Offshoots](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots)|[Offers & Assistance](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance)\n\n\n-\n\n### Ever read the reddiquette? [Take a peek!](/wiki/reddiquette)\n\n[](#/RES_SR_Config/NightModeCompatible)",
                "description_html": '<!-- SC_OFF --><div class="md"><h6><a href="http://www.reddit.com/r/askreddit/submit?selftext=true&amp;title=%5BSerious%5D"> [ SERIOUS ] </a></h6>\n\n<h5><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules">Rules</a>:</h5>\n\n<ol>\n<li><p>You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-">more &gt;&gt;</a></p></li>\n<li><p>Any post asking for advice should be generic and not specific to your situation alone. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is for open-ended discussion questions. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-">more &gt;&gt;</a></p></li>\n<li><p>Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is not your soapbox, personal army, or advertising platform. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-">more &gt;&gt;</a></p></li>\n<li><p>[Serious] tagged posts are off-limits to jokes or irrelevant replies. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">more &gt;&gt;</a></p></li>\n<li><p>Soliciting money, goods, services, or favours is not allowed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-">more &gt;&gt;</a></p></li>\n<li><p>Mods reserve the right to remove content or restrict users&#39; posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-">more &gt;&gt;</a></p></li>\n<li><p>Comment replies consisting solely of images will be removed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-">more &gt;&gt;</a></p></li>\n</ol>\n\n<h5>If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to <a href="https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit">contact the mods</a>, we&#39;re happy to help.</h5>\n\n<hr/>\n\n<h4>Tags to use:</h4>\n\n<blockquote>\n<h2><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">[Serious]</a></h2>\n</blockquote>\n\n<h3>Use a <strong>[Serious]</strong> post tag to designate your post as a serious, on-topic-only thread.</h3>\n\n<h2></h2>\n\n<h4>Filter posts by subject:</h4>\n\n<p><a href="http://ud.reddit.com/r/AskReddit/#ud">Mod posts</a>\n<a href="https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&amp;sort=new&amp;restrict_sr=on&amp;t=all">Serious posts</a>\n<a href="http://bu.reddit.com/r/AskReddit/#bu">Megathread</a>\n<a href="http://nr.reddit.com/r/AskReddit/#nr">Breaking news</a>\n<a href="/r/AskReddit">Unfilter</a></p>\n\n<h2></h2>\n\n<h3>Please use spoiler tags to hide spoilers. <code>&gt;!insert spoiler here!&lt;</code></h3>\n\n<h2></h2>\n\n<h4>Other subreddits you might like:</h4>\n\n<table><thead>\n<tr>\n<th align="left">some</th>\n<th align="left">header</th>\n</tr>\n</thead><tbody>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others">Ask Others</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others">Self &amp; Others</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit">Find a subreddit</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something">Learn something</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta">Meta Subs</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______">What is this ___</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots">AskReddit Offshoots</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance">Offers &amp; Assistance</a></td>\n</tr>\n</tbody></table>\n\n<h2></h2>\n\n<h3>Ever read the reddiquette? <a href="/wiki/reddiquette">Take a peek!</a></h3>\n\n<p><a href="#/RES_SR_Config/NightModeCompatible"></a></p>\n</div><!-- SC_ON -->',
                "display_name": "AskReddit",
                "id": "2qh1i",
                "name": "t5_2qh1i",
                "nsfw": False,
                "public_description": "r/AskReddit is the place to ask and answer thought-provoking questions.",
                "spoilers_enabled": True,
                "subscribers": 32366338,
                "user_is_banned": False,
                "user_is_moderator": False,
                "user_is_subscriber": False,
            },
            "title": "Which song defines your childhood?",
            "type": "submission",
            "upvote_ratio": 1.0,
            "url": "https://www.reddit.com/r/AskReddit/comments/nkcrtr/which_song_defines_your_childhood/",
        }

        test_prefix = ""
        test_pretty_stream = CreatePrettyTable.create()

        try:
            DisplayStream.DisplayStream._populate_table(
                test_include_fields, test_object, test_prefix, test_pretty_stream
            )
            assert True
        except Exception as e:
            print(
                "An exception has occurred when attempting to populate PrettyStream:", e
            )
            assert False


class TestDisplayStreamDisplayMethod:
    """
    Testing DisplayStream class display() method.
    """

    def test_display_method_comment_object(self):
        test_comment_object = {
            "author": "u/Flatworm1",
            "body": "They all went to bed hours ago.",
            "body_html": '<div class="md"><p>They all went to bed hours ago.</p>\n</div>',
            "created_utc": "05-23-2021 20:47:55",
            "distinguished": None,
            "edited": False,
            "id": "gz811x5",
            "is_submitter": False,
            "link_id": "t3_njlm8y",
            "parent_id": "t3_njlm8y",
            "score": 1,
            "stickied": False,
            "submission": {
                "author": "u/Lanre-Haliax",
                "created_utc": "05-23-2021 20:46:39",
                "distinguished": None,
                "edited": False,
                "id": "njlm8y",
                "is_original_content": False,
                "is_self": True,
                "link_flair_text": None,
                "locked": False,
                "name": "t3_njlm8y",
                "nsfw": False,
                "num_comments": 2,
                "permalink": "/r/AskReddit/comments/njlm8y/people_who_where_at_woodstock_in_1969_how_was_it/",
                "score": 4,
                "selftext": "",
                "spoiler": False,
                "stickied": False,
                "subreddit": {
                    "can_assign_link_flair": False,
                    "can_assign_user_flair": False,
                    "created_utc": "01-24-2008 22:52:15",
                    "description": "###### [ [ SERIOUS ] ](http://www.reddit.com/r/askreddit/submit?selftext=true&title=%5BSerious%5D)\n\n\n##### [Rules](https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules):\n1. You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-)\n\n2. Any post asking for advice should be generic and not specific to your situation alone. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-)\n\n3. Askreddit is for open-ended discussion questions. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-)\n\n4. Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-)\n\n5. Askreddit is not your soapbox, personal army, or advertising platform. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-)\n\n6. [Serious] tagged posts are off-limits to jokes or irrelevant replies. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n7. Soliciting money, goods, services, or favours is not allowed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-)\n\n8. Mods reserve the right to remove content or restrict users' posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-)\n\n9. Comment replies consisting solely of images will be removed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-)\n\n##### If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit), we're happy to help.\n\n---\n\n#### Tags to use:\n\n> ## [[Serious]](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n### Use a **[Serious]** post tag to designate your post as a serious, on-topic-only thread.\n\n-\n\n#### Filter posts by subject:\n\n[Mod posts](http://ud.reddit.com/r/AskReddit/#ud)\n[Serious posts](https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&sort=new&restrict_sr=on&t=all)\n[Megathread](http://bu.reddit.com/r/AskReddit/#bu)\n[Breaking news](http://nr.reddit.com/r/AskReddit/#nr)\n[Unfilter](/r/AskReddit)\n\n\n-\n\n### Please use spoiler tags to hide spoilers. `>!insert spoiler here!<`\n\n-\n\n#### Other subreddits you might like:\nsome|header\n:---|:---\n[Ask Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others)|[Self & Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others)\n[Find a subreddit](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit)|[Learn something](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something)\n[Meta Subs](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta)|[What is this ___](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______)\n[AskReddit Offshoots](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots)|[Offers & Assistance](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance)\n\n\n-\n\n### Ever read the reddiquette? [Take a peek!](/wiki/reddiquette)\n\n[](#/RES_SR_Config/NightModeCompatible)",
                    "description_html": '<!-- SC_OFF --><div class="md"><h6><a href="http://www.reddit.com/r/askreddit/submit?selftext=true&amp;title=%5BSerious%5D"> [ SERIOUS ] </a></h6>\n\n<h5><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules">Rules</a>:</h5>\n\n<ol>\n<li><p>You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-">more &gt;&gt;</a></p></li>\n<li><p>Any post asking for advice should be generic and not specific to your situation alone. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is for open-ended discussion questions. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-">more &gt;&gt;</a></p></li>\n<li><p>Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is not your soapbox, personal army, or advertising platform. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-">more &gt;&gt;</a></p></li>\n<li><p>[Serious] tagged posts are off-limits to jokes or irrelevant replies. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">more &gt;&gt;</a></p></li>\n<li><p>Soliciting money, goods, services, or favours is not allowed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-">more &gt;&gt;</a></p></li>\n<li><p>Mods reserve the right to remove content or restrict users&#39; posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-">more &gt;&gt;</a></p></li>\n<li><p>Comment replies consisting solely of images will be removed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-">more &gt;&gt;</a></p></li>\n</ol>\n\n<h5>If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to <a href="https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit">contact the mods</a>, we&#39;re happy to help.</h5>\n\n<hr/>\n\n<h4>Tags to use:</h4>\n\n<blockquote>\n<h2><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">[Serious]</a></h2>\n</blockquote>\n\n<h3>Use a <strong>[Serious]</strong> post tag to designate your post as a serious, on-topic-only thread.</h3>\n\n<h2></h2>\n\n<h4>Filter posts by subject:</h4>\n\n<p><a href="http://ud.reddit.com/r/AskReddit/#ud">Mod posts</a>\n<a href="https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&amp;sort=new&amp;restrict_sr=on&amp;t=all">Serious posts</a>\n<a href="http://bu.reddit.com/r/AskReddit/#bu">Megathread</a>\n<a href="http://nr.reddit.com/r/AskReddit/#nr">Breaking news</a>\n<a href="/r/AskReddit">Unfilter</a></p>\n\n<h2></h2>\n\n<h3>Please use spoiler tags to hide spoilers. <code>&gt;!insert spoiler here!&lt;</code></h3>\n\n<h2></h2>\n\n<h4>Other subreddits you might like:</h4>\n\n<table><thead>\n<tr>\n<th align="left">some</th>\n<th align="left">header</th>\n</tr>\n</thead><tbody>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others">Ask Others</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others">Self &amp; Others</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit">Find a subreddit</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something">Learn something</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta">Meta Subs</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______">What is this ___</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots">AskReddit Offshoots</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance">Offers &amp; Assistance</a></td>\n</tr>\n</tbody></table>\n\n<h2></h2>\n\n<h3>Ever read the reddiquette? <a href="/wiki/reddiquette">Take a peek!</a></h3>\n\n<p><a href="#/RES_SR_Config/NightModeCompatible"></a></p>\n</div><!-- SC_ON -->',
                    "display_name": "AskReddit",
                    "id": "2qh1i",
                    "name": "t5_2qh1i",
                    "nsfw": False,
                    "public_description": "r/AskReddit is the place to ask and answer thought-provoking questions.",
                    "spoilers_enabled": True,
                    "subscribers": 32355402,
                    "user_is_banned": False,
                    "user_is_moderator": False,
                    "user_is_subscriber": False,
                },
                "title": "People who where at Woodstock in 1969, how was it?",
                "type": "submission",
                "upvote_ratio": 1.0,
                "url": "https://www.reddit.com/r/AskReddit/comments/njlm8y/people_who_where_at_woodstock_in_1969_how_was_it/",
            },
            "subreddit_id": "t5_2qh1i",
            "type": "comment",
        }

        try:
            DisplayStream.DisplayStream.display(test_comment_object)
            assert True
        except Exception as e:
            print(
                "An exception has occurred when attempting to display comment in stream:",
                e,
            )
            assert False

    def test_display_method_submission_object(self):
        test_submission_object = {
            "author": "u/NuclearWinterGames",
            "created_utc": "05-24-2021 20:36:44",
            "distinguished": None,
            "edited": False,
            "id": "nkcrtr",
            "is_original_content": False,
            "is_self": True,
            "link_flair_text": None,
            "locked": False,
            "name": "t3_nkcrtr",
            "nsfw": False,
            "num_comments": 0,
            "permalink": "/r/AskReddit/comments/nkcrtr/which_song_defines_your_childhood/",
            "score": 1,
            "selftext": "",
            "spoiler": False,
            "stickied": False,
            "subreddit": {
                "can_assign_link_flair": False,
                "can_assign_user_flair": False,
                "created_utc": "01-24-2008 22:52:15",
                "description": "###### [ [ SERIOUS ] ](http://www.reddit.com/r/askreddit/submit?selftext=true&title=%5BSerious%5D)\n\n\n##### [Rules](https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules):\n1. You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-)\n\n2. Any post asking for advice should be generic and not specific to your situation alone. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-)\n\n3. Askreddit is for open-ended discussion questions. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-)\n\n4. Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-)\n\n5. Askreddit is not your soapbox, personal army, or advertising platform. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-)\n\n6. [Serious] tagged posts are off-limits to jokes or irrelevant replies. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n7. Soliciting money, goods, services, or favours is not allowed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-)\n\n8. Mods reserve the right to remove content or restrict users' posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-)\n\n9. Comment replies consisting solely of images will be removed. [more >>](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-)\n\n##### If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit), we're happy to help.\n\n---\n\n#### Tags to use:\n\n> ## [[Serious]](https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-)\n\n### Use a **[Serious]** post tag to designate your post as a serious, on-topic-only thread.\n\n-\n\n#### Filter posts by subject:\n\n[Mod posts](http://ud.reddit.com/r/AskReddit/#ud)\n[Serious posts](https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&sort=new&restrict_sr=on&t=all)\n[Megathread](http://bu.reddit.com/r/AskReddit/#bu)\n[Breaking news](http://nr.reddit.com/r/AskReddit/#nr)\n[Unfilter](/r/AskReddit)\n\n\n-\n\n### Please use spoiler tags to hide spoilers. `>!insert spoiler here!<`\n\n-\n\n#### Other subreddits you might like:\nsome|header\n:---|:---\n[Ask Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others)|[Self & Others](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others)\n[Find a subreddit](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit)|[Learn something](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something)\n[Meta Subs](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta)|[What is this ___](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______)\n[AskReddit Offshoots](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots)|[Offers & Assistance](https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance)\n\n\n-\n\n### Ever read the reddiquette? [Take a peek!](/wiki/reddiquette)\n\n[](#/RES_SR_Config/NightModeCompatible)",
                "description_html": '<!-- SC_OFF --><div class="md"><h6><a href="http://www.reddit.com/r/askreddit/submit?selftext=true&amp;title=%5BSerious%5D"> [ SERIOUS ] </a></h6>\n\n<h5><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_rules">Rules</a>:</h5>\n\n<ol>\n<li><p>You must post a clear and direct question in the title. The title may contain two, short, necessary context sentences.\nNo text is allowed in the textbox. Your thoughts/responses to the question can go in the comments section. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_1-">more &gt;&gt;</a></p></li>\n<li><p>Any post asking for advice should be generic and not specific to your situation alone. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_2-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is for open-ended discussion questions. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_3-">more &gt;&gt;</a></p></li>\n<li><p>Posting, or seeking, any identifying personal information, real or fake, will result in a ban without a prior warning. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_4-">more &gt;&gt;</a></p></li>\n<li><p>Askreddit is not your soapbox, personal army, or advertising platform. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_5-">more &gt;&gt;</a></p></li>\n<li><p>[Serious] tagged posts are off-limits to jokes or irrelevant replies. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">more &gt;&gt;</a></p></li>\n<li><p>Soliciting money, goods, services, or favours is not allowed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_7-">more &gt;&gt;</a></p></li>\n<li><p>Mods reserve the right to remove content or restrict users&#39; posting privileges as necessary if it is deemed detrimental to the subreddit or to the experience of others. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_8-">more &gt;&gt;</a></p></li>\n<li><p>Comment replies consisting solely of images will be removed. <a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_9-">more &gt;&gt;</a></p></li>\n</ol>\n\n<h5>If you think your post has disappeared, see spam or an inappropriate post, please do not hesitate to <a href="https://www.reddit.com/message/compose?to=%2Fr%2FAskReddit">contact the mods</a>, we&#39;re happy to help.</h5>\n\n<hr/>\n\n<h4>Tags to use:</h4>\n\n<blockquote>\n<h2><a href="https://www.reddit.com/r/AskReddit/wiki/index#wiki_-rule_6-">[Serious]</a></h2>\n</blockquote>\n\n<h3>Use a <strong>[Serious]</strong> post tag to designate your post as a serious, on-topic-only thread.</h3>\n\n<h2></h2>\n\n<h4>Filter posts by subject:</h4>\n\n<p><a href="http://ud.reddit.com/r/AskReddit/#ud">Mod posts</a>\n<a href="https://www.reddit.com/r/AskReddit/search/?q=flair%3Aserious&amp;sort=new&amp;restrict_sr=on&amp;t=all">Serious posts</a>\n<a href="http://bu.reddit.com/r/AskReddit/#bu">Megathread</a>\n<a href="http://nr.reddit.com/r/AskReddit/#nr">Breaking news</a>\n<a href="/r/AskReddit">Unfilter</a></p>\n\n<h2></h2>\n\n<h3>Please use spoiler tags to hide spoilers. <code>&gt;!insert spoiler here!&lt;</code></h3>\n\n<h2></h2>\n\n<h4>Other subreddits you might like:</h4>\n\n<table><thead>\n<tr>\n<th align="left">some</th>\n<th align="left">header</th>\n</tr>\n</thead><tbody>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_ask_others">Ask Others</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_self_.26amp.3B_others">Self &amp; Others</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_find_a_subreddit">Find a subreddit</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_learn_something">Learn something</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_meta">Meta Subs</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_what_is_this______">What is this ___</a></td>\n</tr>\n<tr>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_askreddit_offshoots">AskReddit Offshoots</a></td>\n<td align="left"><a href="https://www.reddit.com/r/AskReddit/wiki/sidebarsubs#wiki_offers_.26amp.3B_assistance">Offers &amp; Assistance</a></td>\n</tr>\n</tbody></table>\n\n<h2></h2>\n\n<h3>Ever read the reddiquette? <a href="/wiki/reddiquette">Take a peek!</a></h3>\n\n<p><a href="#/RES_SR_Config/NightModeCompatible"></a></p>\n</div><!-- SC_ON -->',
                "display_name": "AskReddit",
                "id": "2qh1i",
                "name": "t5_2qh1i",
                "nsfw": False,
                "public_description": "r/AskReddit is the place to ask and answer thought-provoking questions.",
                "spoilers_enabled": True,
                "subscribers": 32366338,
                "user_is_banned": False,
                "user_is_moderator": False,
                "user_is_subscriber": False,
            },
            "title": "Which song defines your childhood?",
            "type": "submission",
            "upvote_ratio": 1.0,
            "url": "https://www.reddit.com/r/AskReddit/comments/nkcrtr/which_song_defines_your_childhood/",
        }

        try:
            DisplayStream.DisplayStream.display(test_submission_object)
            assert True
        except Exception as e:
            print(
                "An exception has occurred when attempting to display submission in stream:",
                e,
            )
            assert False
