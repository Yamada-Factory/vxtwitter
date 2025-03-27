import os

import twExtract
import utils
from vx_testdata import *

def test_twextract_syndicationAPI():
    tweet = twExtract.extractStatus_syndication(testMediaTweet,workaroundTokens=tokens)
    assert utils.stripEndTCO(utils.stripEndTCO(tweet["full_text"]))==testMediaTweet_compare['text']

def test_twextract_extractStatusV2Anon():
    tweet = twExtract.extractStatusV2Anon(testTextTweet,None)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testTextTweet_compare['text']
    tweet = twExtract.extractStatusV2Anon(testVideoTweet,None)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testVideoTweet_compare['text']
    tweet = twExtract.extractStatusV2Anon(testMediaTweet,None)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testMediaTweet_compare['text']
    tweet = twExtract.extractStatusV2Anon(testMultiMediaTweet,None)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])[:94]==testMultiMediaTweet_compare['text'][:94]
    

def test_twextract_v2API():
    tweet = twExtract.extractStatusV2(testMediaTweet,workaroundTokens=tokens)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testMediaTweet_compare['text']

def test_twextract_v2AndroidAPI():
    tweet = twExtract.extractStatusV2Android(testMediaTweet,workaroundTokens=tokens)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testMediaTweet_compare['text']

def test_twextract_extractStatusV2TweetDetails():
    tweet = twExtract.extractStatusV2TweetDetail(testMediaTweet,workaroundTokens=tokens)['legacy']
    assert utils.stripEndTCO(tweet["full_text"])==testMediaTweet_compare['text']

## Tweet retrieve tests ##
def test_twextract_textTweetExtract():
    tweet = twExtract.extractStatus(testTextTweet,workaroundTokens=tokens)
    assert utils.stripEndTCO(tweet["legacy"]["full_text"])==testTextTweet_compare['text']
    assert tweet["user"]["screen_name"]=="jack"
    assert 'extended_entities' not in tweet
    
def test_twextract_extractV2(): # remove this when v2 is default
    tweet = twExtract.extractStatusV2(testTextTweet,workaroundTokens=tokens)

def test_twextract_UserExtract():
    user = twExtract.extractUser(testUser,workaroundTokens=tokens)
    assert user["screen_name"]=="jack"
    assert user["id"]==12
    assert user["created_at"] == "Tue Mar 21 20:50:14 +0000 2006"

def test_twextract_UserExtractID():
    user = twExtract.extractUser(testUserIDUrl,workaroundTokens=tokens)
    assert user["screen_name"]=="jack"
    assert user["id"]==12
    assert user["created_at"] == "Tue Mar 21 20:50:14 +0000 2006"

def test_twextract_UserExtractWeirdURLs():
    for url in testUserWeirdURLs:
        user = twExtract.extractUser(url,workaroundTokens=tokens)
        assert user["screen_name"]=="jack"
        assert user["id"]==12
        assert user["created_at"] == "Tue Mar 21 20:50:14 +0000 2006"

def test_twextract_videoTweetExtract():
    tweet = twExtract.extractStatus(testVideoTweet,workaroundTokens=tokens)
    assert utils.stripEndTCO(tweet["legacy"]["full_text"])==testVideoTweet_compare['text']
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==1
    video = tweet['extended_entities']["media"][0]
    assert video["media_url_https"]==testVideoTweet_compare['media_extended'][0]['thumbnail_url']
    assert video["type"]=="video"
    

def test_twextract_mediaTweetExtract():
    tweet = twExtract.extractStatus(testMediaTweet,workaroundTokens=tokens)
    assert utils.stripEndTCO(tweet['legacy']["full_text"])==testMediaTweet_compare['text']
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==1
    video = tweet['extended_entities']["media"][0]
    
    assert video["media_url_https"]==testMediaTweet_compare['media_extended'][0]['thumbnail_url']
    assert video["type"]=="photo"
    

def test_twextract_multimediaTweetExtract():
    tweet = twExtract.extractStatus(testMultiMediaTweet,workaroundTokens=tokens)
    assert utils.stripEndTCO(tweet['legacy']["full_text"])[:94]==testMultiMediaTweet_compare['text'][:94]
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==3
    video = tweet['extended_entities']["media"][0]
    assert video["media_url_https"]==testMultiMediaTweet_compare["mediaURLs"][0]
    assert video["type"]=="photo"
    video = tweet['extended_entities']["media"][1]
    assert video["media_url_https"]==testMultiMediaTweet_compare["mediaURLs"][1]
    assert video["type"]=="photo"

def test_twextract_pollTweetExtract(): # basic check if poll data exists
    tweet = twExtract.extractStatus("https://twitter.com/norm/status/651169346518056960",workaroundTokens=tokens)
    assert 'card' in tweet
    assert tweet['card']['name']=="poll2choice_text_only"

def test_twextract_NSFW_TweetExtract():
    tweet = twExtract.extractStatus(testNSFWTweet,workaroundTokens=tokens) # For now just test that there's no error

'''
def test_twextract_feed():
    tweet = twExtract.extractUserFeedFromId(testUserID,workaroundTokens=tokens)
'''