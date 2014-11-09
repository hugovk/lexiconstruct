#!/usr/bin/env python
# encoding=utf8
"""
Turn a bunch of archived tweets (eg nixibot.csv) into a dictionary.
For NaNoGenMo/Wordnik Hackathon 2014.
https://github.com/dariusk/NaNoGenMo-2014/
https://github.com/dariusk/wordnik-hackathon
"""
from __future__ import print_function
from operator import itemgetter
from wordnik import *
import collections
import argparse
import inflect
import urllib2
import csv
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Wordnik: get API key at http://developer.wordnik.com/
WORDNIK_API_KEY = "TODO_ENTER_YOURS_HERE"
WORDNIK_USERNAME = "TODO_ENTER_YOURS_HERE"
WORDNIK_PASSWORD = "TODO_ENTER_YOURS_HERE"
WORDNIK_TOKEN = None

wordnik_client = swagger.ApiClient(
    WORDNIK_API_KEY, 'http://api.wordnik.com/v4')
wordApi = WordApi.WordApi(wordnik_client)

DEFS_CACHE = "/Users/hugo/defs_cache.pkl"
DEFS = {}
ATTRIBUTIONS = {}

# For the afterword
DEFS_USED = 0
TOTAL_HEADWORDS = 0
TOTAL_QUOTATIONS = 0


def print_front_page():
    print("### Edition The First")
    print()
    print("### O F")
    print()
    print("# A DICTIONARY OF NOT-A-WORDS")
    print()
    print("### FROM")
    print()
    print("# TWITTER")
    print()
    print("## Of Which A Tweeter")
    print()
    print("### Has Thus DECLARED Such Word Is")
    print()
    print("# NOT A WORD")
    print()
    print("## With Example Usage,")
    print()
    print("### AND A")
    print()
    print("# DEFINITION")
    print()
    print("### Where Available.")
    print()
    print("### Collected Between")
    print()
    print("## OCTOBER 2013")
    print()
    print("### A N D")
    print()
    print("## NOVEMBER 2014.")
    print()
    print("## Compiled by")
    print()
    print("# @hugovk")
    print()
    print("### F O R")
    print()
    print("## NaNoGenMo")
    print()
    print("### A N D")
    print()
    print("## The Wordnik Hackathon")
    print()
    print("### In This Year,")
    print()
    print("# MMXIV")
    print()
    print()


def print_toc():
    print("# Table of Contents")
    print()
    print("1. [Preface](#preface)")
    print()
    print("2. [Top 100](#top-100)")
    print()
    print("3. [The Dictionary](#the-dictionary)")
    print()
    print("4. [Afterword](#afterword)")
    print()
    print("5. [Definitions](#definitions)")
    print()
    print()


def print_preface(mincites):
    p = inflect.engine()
    print("# Preface")
    print()
    print("Each word listed here is the result of someone claiming it is not a word.")
    print()
    print("This dictionary is sourced from tweets containing the text \"X is not a word\", \"X isn't a word\" and \"X ain't a word\", collected between 25th October Oct 25 2013 and 9th November 2014 by [@nixibot](https://twitter.com/nixibot). Only those words with at least " + p.plural("quotation", mincites) + " are included.")
    print()
    print("Where available, a definition is included via Wordnik. Not all words have definitions, and only the first definition is used, which may or not be a different part of speech or the correct defintion. No attempt has been made to correctly categorise them.")
    print()
    print("But what is a word, and what isn't?")
    print()
    print("The editor Stan Carey wrote on his blog [*Sentence first*](http://stancarey.wordpress.com/2014/02/04/not-a-word-prolly-aint-an-argument-anyways/):")
    print()
    print(" > If you see or hear someone reject a word by saying it’s “not a word”, you can reasonably assume that they mean it’s not a word they like, not a word they would use, not a word in standard usage, not a word in a certain dictionary, not a suitable word for the context, and so on. There’s a difference, and it matters. . . .")
    print()
    print("> Word aversion and word hatred are an aesthetic indulgence; word denial is a different beast. Why the cranky resolve to outlaw disliked words? From what imaginary realm do people conjure the authority to decide what’s acceptable?")
    print()
    print("Does inclusion in a dictionary make a word a word?")
    print()
    print("Well, now these words are in a dictionary.")
    print()
    print()


def print_top_100(tweets):
    words = []
    for tweet in tweets:
        words.append(tweet['word'])

    print("# Top 100")
    print()
    print("These are the 100 words most frequently claimed as not-a-word, "
          "shown with the number of claims made.")
    print()
    top = most_frequent_words_and_counts(words, 100)
    for i, (word, count) in enumerate(top):
        print(str(i+1) + ". " + word + " (" + commafy(count) + ")")
    print()
    print()


def most_frequent_words_and_counts(word_list, number=None):
    counter = collections.Counter(word_list)
    most_common = counter.most_common(number)
    return most_common


# Add thousands commas
def commafy(value):
    return "{:,}".format(value)


def print_afterword():
    print("# Afterword")
    print()

    print("This dictionary contains " + commafy(TOTAL_HEADWORDS) +
          " headwords with " + commafy(DEFS_USED) + " definitions and " +
          commafy(TOTAL_QUOTATIONS) + " quotations.")
    print()
    print()


def print_attributions():
    od = collections.OrderedDict(sorted(ATTRIBUTIONS.items()))

    print("# Definitions")
    print()
    print("Definitions powered by Wordnik.")
    print()
    for attribution in od:
        print_it(" * [" + attribution + "] " + od[attribution])
    print()
    print()


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode('utf-8'))


def load_csv(filename):
    with open(filename, mode='rb') as fd:
        data = csv.DictReader(fd)
        rows = []
        seen = set()  # avoid duplicates
        for row in data:
            if row['id_str'] not in seen and row['word'] not in ['actually']:
                seen.add(row['id_str'])
                rows.append(row)
    return rows


def decode_tweet(tweet, key):
    print(type(tweet[key]))
    print(type(tweet[key].decode("cp1252")))
    # return tweet[key]
    return tweet[key].decode("cp1252")


def format_date(date_text):
    # For example:
    # Fri Nov 01 05:19:28 +0000 2013
    # ->
    # 2013 Nov 01
    dd = date_text[8:10]
    mmm = date_text[4:7]
    yyyy = date_text[-4:]
    return(yyyy + " " + mmm + " " + dd)


def process_tweets(tweets):
    global TOTAL_HEADWORDS, TOTAL_QUOTATIONS

    print("# The Dictionary")

    current_word = None
    for tweet in tweets:
        word = tweet['word']
        if current_word != word:
            # New entry
            current_word = word
            TOTAL_HEADWORDS += 1
            print()
            print("**" + word + "**  ")
            print_wordnik_definitions(word)

        if tweet['user_name'] == tweet['screen_name']:
            name = "@" + tweet['user_name']
        else:
            name = tweet['user_name'] + " (@" + tweet['screen_name'] + ")"

        quote = (format_date(tweet['created_at'])
                 + " " + name
                 + ": " + tweet['text'].replace("\r\n", " ") + "  ")
        print(quote)
        TOTAL_QUOTATIONS += 1
    print()
    print()


# TODO: Save token to ini file
def get_wordnik_token():
    import getpass
    if WORDNIK_USERNAME:
        my_username = WORDNIK_USERNAME
    else:
        my_username = raw_input("Enter your Wordnik username: ")
    if WORDNIK_PASSWORD:
        my_password = WORDNIK_PASSWORD
    else:
        my_password = getpass.getpass("Enter your Wordnik password: ")

    accountApi = AccountApi.AccountApi(wordnik_client)
    result = accountApi.authenticate(my_username, my_password)
    token = result.token
#     print("Your Wordnik token is: " + token)
    return token


def load_cache():
    """Load cached Wordnik definitions, saved from a previous run"""
    global DEFS
    if os.path.isfile(DEFS_CACHE):
        with open(DEFS_CACHE, 'rb') as fp:
            DEFS = pickle.load(fp)
#             print("Loaded", len(DEFS), "cached definitions")


def update_cache(word, definitions):
    global DEFS
    DEFS[word] = definitions
    with open(DEFS_CACHE, 'wb') as fp:
        pickle.dump(DEFS, fp, -1)


def format_definitions(definitions):
    global ATTRIBUTIONS, DEFS_USED
    if definitions:
        for d in definitions:
#             print(d.extendedText) # str
#             print(d.text) # str
#             print(d.sourceDictionary) # str
#             print(d.citations) # list[Citation]
#             print(d.labels) # list[Label]
#             print(d.score) # float
#             print(d.exampleUses) # list[ExampleUsage]
#             print(d.attributionUrl) # str
#             print(d.seqString) # str
#             print(d.attributionText) # str
#             print(d.relatedWords) # list[Related]
#             print(d.sequence) # str
#             print(d.word) # str
#             print(d.notes) # list[Note]
#             print(d.textProns) # list[TextPron]
#             print(d.partOfSpeech) # str
            if d.partOfSpeech:
                pos = "*" + d.partOfSpeech + "* "
            else:
                pos = ""
            def_string = (pos + d.text.strip(" ").rstrip(".") +
                          " [" + d.sourceDictionary + "]  ")
            print_it(def_string)
            DEFS_USED += 1
            if d.sourceDictionary not in ATTRIBUTIONS:
                ATTRIBUTIONS[d.sourceDictionary] = d.attributionText


def print_wordnik_definitions(word):
    global WORDNIK_TOKEN
    if WORDNIK_TOKEN is None:
        # Only need to do this once
        WORDNIK_TOKEN = get_wordnik_token()

    if word in DEFS:
        return format_definitions(DEFS[word])

    try:
        definitions = wordApi.getDefinitions(word, limit=1)
    except urllib2.HTTPError:
        # quick fix for 401 invalid response for "friend/bestfriend"
        definitions = None

#     TODO maybe get one of each (main) POS, eg: partOfSpeech='verb' etc.

    update_cache(word, definitions)

    format_definitions(definitions)


def filter_min_cites(tweet, mincites):
    """ Keep only those words with at least X cites"""
    if mincites == 1:
        return tweets

    temp_list = []
    last_word = None
    kept_tweets = []
    for tweet in tweets:
        word = tweet['word']
        if word == last_word:
            temp_list.append(tweet)
        else:
            if len(temp_list) >= mincites:
                kept_tweets.extend(temp_list)
            temp_list = []
        last_word = word
    return kept_tweets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a dictionary from archived tweets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-c', '--csv', default='/Users/hugo/Dropbox/bin/data/nixibot.csv',
        help='Input CSV file')
    parser.add_argument(
        '-n', '--mincites',  type=int, default=4,
        help="Only include entries with this minimum number of cites")
    args = parser.parse_args()

    print_front_page()
    print_toc()
    print_preface(args.mincites)

    tweets = load_csv(args.csv)

    # Sort by word
    tweets = sorted(tweets, key=itemgetter('word'))
#     print("Total tweets:", len(tweets))

    tweets = filter_min_cites(tweets, args.mincites)

    print_top_100(tweets)

    load_cache()
    process_tweets(tweets)

    print_afterword()
    print_attributions()

# End of file
