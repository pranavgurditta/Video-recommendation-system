# -*- coding: utf-8 -*-
"""running_youtube.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16msIKghLrTyv6PAkx8FPrw5MO6vACAab
    
    Some references have been taken from https://www.kdnuggets.com/2018/08/practitioners-guide-processing-understanding-text-2.html, other resources.
"""
import sys
import en_core_web_sm
import pandas as pd
import pprint
import matplotlib.pyplot as pd

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


import spacy
import warnings
warnings.filterwarnings("ignore")

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
import re
from bs4 import BeautifulSoup
import unicodedata
from afinn import Afinn
afn=Afinn(emoticons=True)

nltk.download('stopwords',halt_on_error=False)
from nltk.corpus import sentiwordnet as swn
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

import pyLDavis
datetimeFormat= '%Y-%m-%d %H:%M:%S.%f'

nlp=spacy.load('en_core_web_sm')
tokenizer=ToktokTokenizer()

np.set_printoptions(precision=2,linewidth=80)
def strip_html_tags(text):
    '''To strip HTML tags using Beautiful Soup'''
    
    soup=BeautifulSoup(text,"htmp.parser")
    stripped_text=soup.get_text();
    return stripped_text

def remove_accented_chars(text):
    '''To remove accented characters, accented characters are converted and standardized into ASCII characters'''
    text=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('utf-8','ignore')
    return text

CONTRACTION_MAP = {
"ain't": "is not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he would",
"he'd've": "he would have",
"he'll": "he will",
"he'll've": "he will have",
"he's": "he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how is",
"I'd": "I would",
"I'd've": "I would have",
"I'll": "I will",
"I'll've": "I will have",
"I'm": "I am",
"I've": "I have",
"i'd": "i would",
"i'd've": "i would have",
"i'll": "i will",
"i'll've": "i will have",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it would",
"it'd've": "it would have",
"it'll": "it will",
"it'll've": "it will have",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she would",
"she'd've": "she would have",
"she'll": "she will",
"she'll've": "she will have",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so as",
"that'd": "that would",
"that'd've": "that would have",
"that's": "that is",
"there'd": "there would",
"there'd've": "there would have",
"there's": "there is",
"they'd": "they would",
"they'd've": "they would have",
"they'll": "they will",
"they'll've": "they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what'll've": "what will have",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"when's": "when is",
"when've": "when have",
"where'd": "where did",
"where's": "where is",
"where've": "where have",
"who'll": "who will",
"who'll've": "who will have",
"who's": "who is",
"who've": "who have",
"why's": "why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you would",
"you'd've": "you would have",
"you'll": "you will",
"you'll've": "you will have",
"you're": "you are",
"you've": "you have"
}

def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    '''
    Expanding Contractions¶
    In the English language, contractions are basically shortened versions of words or syllables.
    Contractions pose a problem in text normalization because we have to deal with special characters like the apostrophe
    and we also have to convert each contraction to its expanded, original form.
    Our expand_contractions(...) function uses regular expressions and various contractions mapped to expand all contractions in our text corpus.
    '''

    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                           flags=re.IGNORECASE|re.DOTALL) #re.compile takes and argument and flags and converts the argument to a pattern object,for example
                           # the pattern object has pattern (are'nt | haven't |...) and as flag has IGNORECASE enable [A-Z] can map to small a to z too and
                           # DOTALL allows '.' to refer every character and new line too.


    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match)\
                                if contraction_mapping.get(match)\
                                else contraction_mapping.get(match.lower())
        expanded_contraction = first_char+expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'","", expanded_text)
    return expanded_text

def remove_special_characters(text):
    '''
    Removing Special Characters
    Simple regexes can be used to achieve this. Our function remove_special_characters(...) helps us remove special characters.
    In our code, we have retained numbers but you can also remove numbers if you do not want them in your normalized corpus.
    '''
    text = re.sub(r'[^a-zA-z0-9\s]', '', text)
    return text

def lemmatize_text(text):
    '''
    Lemmatizing text
    Word stems are usually the base form of possible words that can be created by attaching affixes like prefixes and
    suffixes to the stem to create new words. This is known as inflection. The reverse process of obtaining the base form of a
    word is known as stemming. The nltk package offers a wide range of stemmers like the PorterStemmer and LancasterStemmer.
    Lemmatization is very similar to stemming, where we remove word affixes to get to the base form of a word. However the base
    form in this case is known as the root word but not the root stem. The difference being that the root word is always a
    lexicographically correct word, present in the dictionary, but the root stem may not be so. We will be using lemmatization only
    in our normalization pipeline to retain lexicographically correct words. The function lemmatize_text(...) helps us with this aspect
    '''
    text = nlp(text)
    text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
    return text

stopword_list = nltk.corpus.stopwords.words('english')
stopword_list.remove('no')
stopword_list.remove('not')

def remove_stopwords(text, is_lower_case=False):
    '''

    Words which have little or no significance especially when constructing meaningful features from text
    are also known as stopwords or stop words. These are usually words that end up having the maximum frequency if you do
     a simple term or word frequency in a document corpus. Words like a, an, the, and so on are considered to be stopwords.
     There is no universal stopword list but we use a standard English language stopwords list from nltk. You can also add
      your own domain specific stopwords if needed.
    The function remove_stopwords(...) helps us remove stopwords and retain words having the most significance and context in a corpus.
    '''
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

def normalize_corpus(corpus, html_stripping=True, contraction_expansion=True,
                     accented_char_removal=True, text_lower_case=True,
                     text_lemmatization=True, special_char_removal=True,
                     stopword_removal=True):

    normalized_corpus = []
    # normalize each document in the corpus
    doc=corpus
        # strip HTML
    if html_stripping:
        doc = strip_html_tags(doc)

        # remove accented characters
    if accented_char_removal:
        doc = remove_accented_chars(doc)
        # expand contractions
    if contraction_expansion:
        doc = expand_contractions(doc)
        # lowercase the text
    if text_lower_case:
        doc = doc.lower()
        # remove extra newlines
    doc = re.sub(r'[\r|\n|\r\n]+', ' ',doc)
        # insert spaces between special characters to isolate them
    special_char_pattern = re.compile(r'([{.(-)!}])')
    doc = special_char_pattern.sub(" \\1 ", doc)
        # lemmatize text
    if text_lemmatization:
        doc = lemmatize_text(doc)
        # remove special characters
    if special_char_removal:
        doc = remove_special_characters(doc)
        # remove extra whitespace
    doc = re.sub(' +', ' ', doc)
        # remove stopwords
    if stopword_removal:
        doc = remove_stopwords(doc, is_lower_case=text_lower_case)

    normalized_corpus.append(doc)

    return doc

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def score_reviews(reviews):
    score_list = []
    overall_score = 0
    analyser = SentimentIntensityAnalyzer()
    for review in reviews:
        score = analyser.polarity_scores(review)
        #print(str(score))
        score_list.append(score['compound'])
    #print(score_list)
    for compound_score in score_list:
        overall_score = overall_score + compound_score
    return (overall_score/len(score_list))

DEVELOPER_KEY = "AIzaSyBYCuNavpfCtQkfE_seJrK91W55UveOleQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
def main(topic):
    keyword_user=topic

    request = youtube.search().list(part="id,snippet",maxResults=10,q=keyword_user)
    video_links=[]
    response = request.execute()
    print(response['items'])
    for item in response['items']:
        print("the video links are")
        if('videoId' in item['id']):
          video_links.append(item['id']['videoId'])
          print(item['id']['videoId'])
          c=0
    video_rating_comment_based=[]
    for video in video_links:
        try:
          request = youtube.commentThreads().list(part="snippet,replies",videoId=video)
          comments_of_single_video = request.execute()
        except:
          video_rating_comment_based.append(-999999)
          continue

        print("The comments are")
        comments_to_evaluate=[]
        for single_comment in comments_of_single_video['items']:
            a = normalize_corpus(single_comment['snippet']['topLevelComment']['snippet']['textDisplay'])
            print((a))
            comments_to_evaluate.append(a)

        print(score_reviews(comments_to_evaluate))
        video_rating_comment_based.append(score_reviews(comments_to_evaluate))
    url_rating_dict={}
    for url in video_links:
      for rating in video_rating_comment_based:
        url_rating_dict[url]=rating
        video_rating_comment_based.remove(rating)
        break
    url_rating_dict=sorted(url_rating_dict.items(), key = lambda kv: kv[1], reverse = True)[:5]
    return (url_rating_dict)

def remNonChar(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

