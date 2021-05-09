# The Forest

## Table of Contents

* [Introduction](#introduction)
    + [Motivation](#motivation)
    + [Inspiration](#inspiration)
* [How the Forest Works](#how-the-forest-works)
    + [The `CommentNode`](#the-commentnode)
    + [The `Forest`](#the-forest-1)
    + [Serializing the `Forest`](#serializing-the-forest)

## Introduction

### Motivation

I am a self-taught software developer who just recently graduated from college and am currently looking for my first full-time job. I do not have a computer science degree, so I have had to teach myself a ton of concepts that I would have learned if I got the degree. A class I wish I was able to take in college is data structures and algorithms because that seems to be all the buzz when it comes to the technical interview, which I unfortunately struggle with greatly due to my lack of experience and practice.

Recently (March 2021) I have been teaching myself DSA. Implementing simple examples of each topic within DSA was not so bad (I am currently working on a study guide/reference repository containing these implementations in both Python and Rust that I will make public soon), but practicing Leetcode problems was and still is a difficult process for me. I will continue to power through the struggle because my livelihood and future career depends on it, though. 

While it has not been a smooth journey, I have come to realize how useful DSA is and am implementing what I have learned in a real-world use case. I do not think I would have been able to figure out a solution to the structured comments scraper's prior shortcomings if I had not studied this area within computer science. I recently implemented my first [trie][trie] and was fascinated by how abstract data structures worked. I immediately realized I needed to use a tree data structure for the structured comments scraper in order to take it to the next level, which is the purpose of [this pull request][Pull Request].

### Inspiration

The `Forest` is named after PRAW's [`CommentForest`][CommentForest]. The `CommentForest` does not return comments in structured format, so I wrote my own implementation of it.

The trie was a huge inspiration for the `Forest`. I will quickly explain my implementation of the trie node.

```python
class TrieNode():
    def __init__(self, char, is_word):
        self.char = char
        self.is_word = is_word
        self.children = dict()
```

Each node of the trie contains a character, a boolean flag indicating whether the node denotes the end of a word, and holds a dictionary filled with child nodes as values and their respective characters as keys. I could have used an array and the indices within it to emulate a dictionary, but I figured I could save some access time at the cost of extra space.

Anyways, the trie implementation is very similar to how the `Forest` works.

## How the Forest Works

I will strip docstring comments from the source code to keep it relatively short.

### The `CommentNode`

I created a class `CommentNode` to store each comment's metadata and replies:

```python
class CommentNode():
    def __init__(self, metadata):
        for key, value in metadata.items():
            self.__setattr__(key, value)

        self.replies = []
```

I used `__setattr__()` because the root node defers from the standard comment node schema. By using `__setattr__()`, `CommentNode` attributes will be dynamically set based on the `metadata` dictionary that has been passed in. `self.replies` holds additional `CommentNode`s.

### The `Forest`

Next, I created a class `Forest` which holds the root node and includes methods for insertion.

**The Root Node**

First, let's go over the root node.

```python
class Forest():
    def __init__(self):
        self.root = CommentNode({ "id": "abc123" })
```

The only key in the dictionary passed into `CommentNode` is `id`, therefore the root `CommentNode` will only contain the attributes `self.id` and `self.replies`. A mock submission ID is shown. The actual source code will pull the submission's ID based on the URL that was passed into the `-c` flag and set the `id` value accordingly.

Before I get to the insertion methods, I will explain how comments and their replies are linked.

**How PRAW Comments Are Linked**

PRAW returns all submission comments by level order. This means all top levels are returned first, followed by all second-level replies, then third, so on and so forth.

I will create some mock comment objects to demonstrate. Here is a top level comment corresponding to the mock submisssion ID. Note the `parent_id` contains the submission's `id`, which is stored in `self.root.id`:

```json
{
    "author": "u/asdfasdfasdfasdf",
    "body": "A top level comment here.",
    "created_utc": "06-06-2006 06:06:06",
    "distinguished": null,
    "edited": false,
    "id": "qwerty1",
    "is_submitter": false,
    "link_id": "t3_asdfgh",
    "parent_id": "t3_abc123",
    "score": 666,
    "stickied": false
}
```

Here is a second-level reply to the top comment. Note the `parent_id` contains the top comment's `id`:

```json
{
    "author": "u/hjklhjklhjklhjkl",
    "body": "A reply here.",
    "created_utc": "06-06-2006 18:06:06",
    "distinguished": null,
    "edited": false,
    "id": "hjkl234",
    "is_submitter": true,
    "link_id": "t3_1a2b3c",
    "parent_id": "t1_qwerty1",
    "score": 6,
    "stickied": false
}
```

This pattern continues all the way down to the last level of comments. It is now very easy to link the correct comments together. I do this by calling `split("_", 1)` on the `parent_id` and then getting the second item in the split list to compare values. I also specify the `maxsplit` parameter to force one split.

**The Insertion Methods**

I then defined the methods for `CommentNode` insertion.

```python
    def _dfs_insert(self, new_comment):
        stack = []
        stack.append(self.root)
        
        visited = set()
        visited.add(self.root)

        found = False
        while not found:
            current_comment = stack.pop(0)
            
            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.id:
                    reply.replies.append(new_comment)
                    found = True
                else:
                    if reply not in visited:
                        stack.insert(0, reply)
                        visited.add(reply)

    def seed(self, new_comment):
        parent_id = new_comment.parent_id.split("_", 1)[1]

        self.root.replies.append(new_comment) \
            if parent_id == getattr(self.root, "id") \
            else self._dfs_insert(new_comment)
```

I implemented the [depth-first search][Depth-First Search] algorithm to find a comment's parent node and insert it into the parent node's `replies` array. I defined a separate `visited` set to keep track of visited `CommentNode`s to avoid an infinite loop of inserting `CommentNode`s that were already visited into the `stack`. At first I wrote a recursive version of depth-first search, but then opted for an iterative version because it would not scale well for submissions that included large amounts of comments, ie. stack overflow.

Within the `seed` method, I first check if the `CommentNode` is a top level comment by comparing its parent ID to the submission ID. Depth-first search is triggered if the `CommentNode` is not a top level comment.

### Serializing the `Forest`

Since Python's built-in JSON module can only handle primitive types that have a direct JSON equivalent, a custom encoder is necessary to convert the `Forest` into JSON format. I defined this in `Export.py`.

```python
from json import JSONEncoder

class EncodeNode(JSONEncoder):
    def default(self, object):
        return object.__dict__
```

The `default()` method overrides `JSONEncoder`'s `default()` method and serializes the `CommentNode` by converting it into a dictionary, which is a primitive type that has a direct JSON equivalent:

```python
EncodeNode().encode(CommentNode)
```

This ensures the node is correctly encoded before I call the `seed()` method to insert a new `CommentNode` into the `replies` arrays of its respective parent `CommentNode`.

I can then use this custom `JSONEncoder` subclass while exporting by specifying it within `json.dump()` with the `cls` kwarg:

```python
with open(filename, "w", encoding = "utf-8") as results:
    json.dump(data, results, indent = 4, cls = EncodeNode)
```

This was how the structured comments export was implemented. Refer to the source code located in `urs/praw_scrapers/Comments.py` to see more. I hope this was somewhat interesting and/or informative. Thanks for reading!

<!-- LINKS -->
[Pull Request]: https://github.com/JosephLai241/URS/pull/24

[CommentForest]: https://praw.readthedocs.io/en/latest/code_overview/other/commentforest.html
[trie]: https://www.interviewcake.com/concept/java/trie
[Depth-First Search]: https://www.interviewcake.com/concept/java/dfs
