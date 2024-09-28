# this project involves generating prefix trees for words 

import doctest
from text_tokenize import tokenize_sentences


def check_valid_key(key):
    if not isinstance(key, str):
        raise TypeError

class PrefixTree:
    """
    PrefixTree objects represent individual nodes in a prefix tree
    """
    def __init__(self):
        self.value = None
        self.children = {}

    def get_prefix_tree(self, key):
        current = self
        for node in key:
            if node in current.children:
                current = current.children[node]
            else:
                raise KeyError
        return current

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        check_valid_key(key)
        current = self
        for node in key:
            if node not in current.children:
                current.children[node] = PrefixTree()
            current = current.children[node]
        current.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        check_valid_key(key)
        item_value = self.get_prefix_tree(key).value
        if item_value is not None:
            return item_value
        else:
            raise KeyError

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        check_valid_key(key)
        current = self.get_prefix_tree(key)
        if current.value is not None:
            current.value = None
        else:
            raise KeyError

    def present_node(self, key):
        try:
            self.get_prefix_tree(key)
        except KeyError:
            return False
        return True

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        check_valid_key(key)
        try:
            current = self.get_prefix_tree(key)
        except KeyError:
            return False
        if current.value is not None:
            return True
        return False

    def __iter__(self):
        def helper(self, prefix):
            if self.value is not None:
                yield (prefix, self.value)
            for letter, child in self.children.items():
                yield from helper(child, prefix+letter)
        yield from helper(self, "")


def create_frequency_dict(sentences):
    frequency_dict = {}
    for sentence in sentences:
        word_list = sentence.split()
        for word in word_list:
            frequency_dict.setdefault(word, 0)
            frequency_dict[word] += 1
    return frequency_dict


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    sentences = tokenize_sentences(text)
    word_frequency_dict = create_frequency_dict(sentences)
    prefix_tree = PrefixTree()
    for word, frequency in word_frequency_dict.items():
        prefix_tree[word] = frequency
    return prefix_tree


def remove_tuple(prefix, subtree_list):
    return [prefix + subtree[0] for subtree in subtree_list]


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError
    if not tree.present_node(prefix):
        return []
    subtree_list = list(tree.get_prefix_tree(prefix))
    if prefix in tree:
        subtree_list.append(("", tree[prefix]))
    subtree_list = sorted(subtree_list, key=lambda x: x[1], reverse=True)
    if max_count is None:
        return remove_tuple(prefix, subtree_list)
    return remove_tuple(prefix, subtree_list[:max_count])


def single_char_insertion(tree, word):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(word) + 1):
        for letter in alphabet:
            potential_word = word[:i] + letter + word[i:]
            if potential_word in tree:
                yield (potential_word, tree[potential_word])


def single_char_deletion(tree, word):
    for i in range(len(word)):
        potential_word = word[:i] + word[i + 1 :]
        if potential_word in tree:
            yield (potential_word, tree[potential_word])


def single_char_replacement(tree, word):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i, _ in enumerate(word):
        for letter in alphabet:
            if letter != word[i]:
                potential_word = word[:i] + letter + word[i + 1 :]
                if potential_word in tree:
                    yield (potential_word, tree[potential_word])

def transpose(tree, word):
    for i in range(len(word) - 1):
        potential_word = word[:i] + word[i + 1] + word[i] + word[i + 2 :]
        if potential_word in tree:
            yield (potential_word, tree[potential_word])


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    autocomplete_set = set(autocomplete(tree, prefix, max_count))
    if max_count is not None and len(autocomplete_set) >= max_count:
        return autocomplete_set
    valid_edits = set()
    for function in (single_char_insertion, single_char_deletion, 
                     single_char_replacement, transpose):
        valid_edits.update({edit for edit in function(tree, prefix) 
                            if edit[0] not in autocomplete_set})
    sorted_edits = sorted(list(valid_edits), key=lambda x: x[1], reverse=True)
    if max_count is None:
        return list(autocomplete_set) + [edit[0] for edit in sorted_edits]
    return list(autocomplete_set) + [
        edit[0] for edit in sorted_edits[: (max_count - len(autocomplete_set))]
    ]


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if pattern == "" and tree.value is None:
        return []
    if pattern == "" and tree.value is not None:
        return [("", tree.value)]
    first, rest = pattern[0], pattern[1:]
    if first not in tree.children and first != "*" and first != "?":
        return []
    if first not in ("*", "?"):
        return [
            (first + word[0], word[1])
            for word in word_filter(tree.children[first], rest)
        ]
    elif first == "?":
        return [
            (child + word[0], word[1])
            for child in tree.children
            for word in word_filter(tree.children[child], rest)
        ]
    else:
        star_list = []
        star_list.extend(
            [word for word in word_filter(tree, rest) if word not in star_list]
        )
        for child in tree.children:
            star_list.extend(
                [
                    (child + word[0], word[1])
                    for word in word_filter(tree.children[child], pattern)
                    if (child + word[0], word[1]) not in star_list
                ]
            )
        return star_list

if __name__ == "__main__":
    doctest.testmod()
