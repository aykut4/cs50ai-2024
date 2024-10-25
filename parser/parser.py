import nltk
from nltk.tokenize import word_tokenize
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""
# Det Adj Adj Adj N P Det N P Det N
# p det n adv
#| N V Det N | N V Det N P N | N V P Det Adj Adj N
NONTERMINALS = """
S -> NP | VP | NP VP | S Conj S | VP NP
NP -> N | N NP | NP NP | Adj NP | N Adv | Det N | Det N P N | P Det NP | Det NP | P NP | Adv NP
VP -> V | V P | V NP | Adv VP | V Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    sentence = sentence.strip()
    # sentence = [word[:-1] for word in sentence if word[-1] == '.' else word]
    #for word in sentence:
    #    if word[-1] == ".":
    #        word = word[:-1]
    sentence = sentence.lower()
    words = sentence.split()
    filtered_words = [word for word in words if re.match("[a-zA-Z]", word)]
    sentence = ' '.join(filtered_words)
    sentence = word_tokenize(sentence)
    sentence = [word for word in sentence if word != '.']
    print(sentence)
    return sentence


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunks = []
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            if not any(child.label() == 'NP' for child in subtree.subtrees(lambda t: t != subtree)):
                np_chunks.append(subtree)
    return np_chunks


if __name__ == "__main__":
    main()
