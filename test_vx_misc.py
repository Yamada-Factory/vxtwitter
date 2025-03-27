import twitfix, cache, twExtract
from vx_testdata import *
from twExtract import twUtils

def test_calcSyndicationToken():
    assert twUtils.calcSyndicationToken("1691389765483200513") == "43lnobuxzql"

def test_addToCache():
    cache.clearCache()
    twitfix.getTweetData(testTextTweet)
    twitfix.getTweetData(testVideoTweet)
    twitfix.getTweetData(testMediaTweet)
    twitfix.getTweetData(testMultiMediaTweet)
    #retrieve
    compareDict(videoRedirect(testTextTweet_compare),videoRedirect(cache.getVnfFromLinkCache(testTextTweet)))
    compareDict(videoRedirect(testVideoTweet_compare),videoRedirect(cache.getVnfFromLinkCache(testVideoTweet)))
    compareDict(videoRedirect(testMediaTweet_compare),videoRedirect(cache.getVnfFromLinkCache(testMediaTweet)))
    compareDict(videoRedirect(testMultiMediaTweet_compare),videoRedirect(cache.getVnfFromLinkCache(testMultiMediaTweet)))
    cache.clearCache()