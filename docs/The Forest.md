# The Forest

## Introduction

### Motivation

I am a self-taught software developer who just recently graduated from college and am currently looking for my first full-time job. I do not have a computer science degree, so I have had to teach myself a ton of concepts that I would have learned if I got the degree. A class I wish I was able to take in college is data structures and algorithms because that seems to be all the buzz when it comes to the technical interview, which I unfortunately struggle with greatly due to my lack of experience and practice.

Recently I have been teaching myself DSA. Implementing simple examples of each topic within DSA was not so bad (I am currently working on a study guide/reference repository containing these implementations in both Python and Rust that I will make public soon), but practicing Leetcode problems was and still is a difficult process for me. I will continue to power through the struggle because my livelihood and future career depends on it, though. 

While it has not been a smooth journey, I have come to realize how useful DSA is and am implementing what I have learned in a real-world use case. I do not think I would have been able to figure out a solution to the structured comments scraper's prior shortcomings if I had not studied this area within computer science. I recently implemented my first [trie][trie] and was fascinated by how abstract data structures worked. I immediately realized I needed to use a tree data structure for the structured comments scraper in order to take it to the next level, which is the purpose of [this pull request][Pull Request].

### Inspiration

The `Forest` is named after PRAW's [`CommentForest`][CommentForest]. The `CommentForest` does not return comments in structured format, so I wrote my own implementation of it.

The trie was a huge inspiration to the `Forest`. I will quickly explain my implementation of the trie node.

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

I will strip docstring comments from the source code to keep it short.

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

The only key in the dictionary passed into `CommentNode` is `id`, therefore the root `CommentNode` will only contain the attributes `self.id` and `self.replies`. A mock submission ID I typed is shown. 

Before I get to the insertion methods, I will explain how comments and their replies are linked.

**How PRAW Comments Are Linked**

PRAW returns all submission comments by level order. This means all top levels are returned first, followed by all second-level replies, then third, so on and so forth.

Here is a mock top comment corresponding to the mock submisssion ID. Note the `parent_id` contains the mock submission ID:

```
{
    'parent_id': 't3_abc123', 
    'comment_id': 'qwerty1', 
    'author': 'someone', 
    'date_created': '06-06-2006 06:06:06', 
    'upvotes': 666, 
    'text': 'some text here', 
    'edited': False, 
    'is_submitter': False, 
    'stickied': False
}
```

Here is a mock second-level reply to the mock top comment. Note the `parent_id` contains the mock top comment's comment ID:

```
{
    'parent_id': 't1_qwerty1', 
    'comment_id': 'hjkl234', 
    'author': 'someone', 
    'date_created': '06-06-2006 18:06:06', 
    'upvotes': 6, 
    'text': 'a reply here', 
    'edited': False, 
    'is_submitter': True, 
    'stickied': False
}
```

This pattern continues all the way down to the last level of comments. It is now very easy to link the correct comments together. I do this by calling `split("_", 1)` on the `parent_id` and then getting the second item in the split list to compare values. I also specify the `maxsplit` parameter to force one split.

**The Insertion Methods**

I then defined the methods for `CommentNode` insertion.

```python
    def _dfs_insert(self, existing_comment, new_comment):
        stack = []
        stack.append(existing_comment)
        
        visited = set()
        visited.add(existing_comment)

        found = False
        while not found:
            current_comment = stack.pop(0)
            
            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.comment_id:
                    reply.replies.append(new_comment)
                    found = True
                else:
                    if reply not in visited:
                        stack.insert(0, reply)
                        visited.add(reply)

    def seed(self, new_comment):
        parent_id = new_comment.parent_id.split("_", 1)[1]
                
        if parent_id == getattr(self.root, "id"):
            self.root.replies.append(new_comment)
        else:
            self._dfs_insert(self.root, new_comment)
```

I implemented the [depth-first search][Depth-First Search] algorithm to find a comment's parent node and insert it into the parent node's `replies` array. I defined a separate `visited` set to keep track of visited `CommentNode`s to avoid an infinite loop of inserting `CommentNode`s that were already visited. I wrote a recursive version of depth-first search, but then opted for an iterative version because it would not scale well for submissions that included large amounts of comments, ie. stack overflow.

Within the `seed` method, I first check if the `CommentNode` is a top level comment by comparing its parent ID to the submission ID. Depth-first search is triggered if the `CommentNode` is not a top level comment.

### Serializing the Forest

Since Python's built-in JSON module can only handle primitive types that have a direct JSON equivalent, a custom encoder is necessary to convert the `Forest` into JSON format. I defined this in `Export.py`.

```python
from json import JSONEncoder

class EncodeNode(JSONEncoder):
    """
    Methods to serialize CommentNodes for JSON export. 
    """

    def default(self, object):
        """
        Override the default JSONEncoder `default()` method. 
        """

        return object.__dict__
```

The `default()` method overrides `JSONEncoder`'s `default()` method and serializes the `CommentNode`. By doing this, I convert the `CommentNode` into a dictionary, which is a primitive type that has a direct JSON equivalent. Each node will be converted into dictionary format when inserted into the `replies` array by writing:

```python
EncodeNode().encode(CommentNode)
```

I can then use this custom `JSONEncoder` subclass while exporting by specifying it within `json.dump()` with the `cls` kwarg:

```python
with open(filename, "w", encoding = "utf-8") as results:
    json.dump(data, results, indent = 4, cls = EncodeNode)
```

That's all!

<!-- LINKS -->
[Pull Request]: https://something.com

[CommentForest]: https://praw.readthedocs.io/en/latest/code_overview/other/commentforest.html
[trie]: https://www.interviewcake.com/concept/java/trie
[Depth-First Search]: https://www.interviewcake.com/concept/java/dfs
