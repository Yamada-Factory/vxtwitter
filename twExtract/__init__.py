import uuid
import json
import requests
import re
import os
import random
import urllib.parse
import math
from oauthlib import oauth1
bearer="Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
v2bearer="Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
androidBearer="Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F"
tweetdeckBearer="Bearer AAAAAAAAAAAAAAAAAAAAAFQODgEAAAAAVHTp76lzh3rFzcHbmHVvQxYYpTw%3DckAlMINMjmCwxUcaXbAN4XqJVdgMJaHqNOFgPMK0zN1qLqLQCF"

bearerTokens=[tweetdeckBearer,bearer,v2bearer,androidBearer]

guestToken=None
guestTokenUses=0
pathregex = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"
userregex = r"^https?:\/\/(?:www\.)?twitter\.com\/(?:#!\/)?@?([^/?#]*)(?:[?#/].*)?$"
userIDregex = r"\/i\/user\/(\d+)"

v2Features='{"longform_notetweets_inline_media_enabled":true,"super_follow_badge_privacy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"super_follow_user_api_enabled":true,"super_follow_tweet_api_enabled":true,"android_graphql_skip_api_media_color_palette":true,"creator_subscriptions_tweet_preview_api_enabled":true,"freedom_of_speech_not_reach_fetch_enabled":true,"creator_subscriptions_subscription_count_enabled":true,"tweetypie_unmention_optimization_enabled":true,"longform_notetweets_consumption_enabled":true,"subscriptions_verification_info_enabled":true,"blue_business_profile_image_shape_enabled":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"super_follow_exclusive_tweet_notifications_enabled":true}'
v2graphql_api="2OOZWmw8nAtUHVnXXQhgaA"

v2AnonFeatures='{"creator_subscriptions_tweet_preview_api_enabled":true,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"tweet_with_visibility_results_prefer_gql_media_interstitial_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_enhance_cards_enabled":false}'
v2AnonGraphql_api="7xflPyRiUxGVbJd4uWmbfg"
gt_pattern = r'document\.cookie="gt=([^;]+);'

androidGraphqlFeatures='{"longform_notetweets_inline_media_enabled":true,"super_follow_badge_privacy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"super_follow_user_api_enabled":true,"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled":true,"super_follow_tweet_api_enabled":true,"articles_api_enabled":true,"android_graphql_skip_api_media_color_palette":true,"creator_subscriptions_tweet_preview_api_enabled":true,"freedom_of_speech_not_reach_fetch_enabled":true,"tweetypie_unmention_optimization_enabled":true,"longform_notetweets_consumption_enabled":true,"subscriptions_verification_info_enabled":true,"blue_business_profile_image_shape_enabled":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"immersive_video_status_linkable_timestamps":true,"super_follow_exclusive_tweet_notifications_enabled":true}'
androidGraphql_api="llQH5PFIRlenVrlKJU8jNA"

tweetDetailGraphqlFeatures='{"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}'
tweetDetailGraphql_api="e7RKseIxLu7HgkWNKZ6qnw"

twitterUrl = "x.com" # doubt this will change but just in case
class TwExtractError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.msg = message

    def __str__(self):
        return self.msg

def cycleBearerTokenGet(url,headers):
    global bearerTokens
    rateLimitRemaining = None
    for token in bearerTokens:
        headers["Authorization"] = token
        try:
            tweet = requests.get(url, headers=headers)
            try:
                rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
            except: # for some reason the header is not always present
                pass
            if tweet.status_code == 429 and rateLimitRemaining is not None and int(rateLimitRemaining) > 0: # special case where the bearer token is rate limited but another one is not
                # try another bearer token
                print(f"Error 429 but {rateLimitRemaining} remaining")
                continue
            else:
                # move successful token to the front if it's not already there
                if token != bearerTokens[0]:
                    bearerTokens.insert(0,bearerTokens.pop(bearerTokens.index(token)))
                return tweet
        except Exception as e:
            pass
        return tweet
    raise TwExtractError(400, "Extract error")

def twitterApiGet(url,btoken=None,authToken=None,guestToken=None):

    if authToken.startswith("oa|"):
        url = url.replace("https://x.com/i/api/graphql/","https://api.twitter.com/graphql/")
        authToken = authToken[3:]
        key = authToken.split("|")[0]
        secret = authToken.split("|")[1]

        twt = oauth1.Client(client_key='3nVuSoBZnx6U4vzUxf5w',client_secret='Bcs59EFbbsdF6Sl9Ng71smgStWEGwXXKSjYvPVt7qys',resource_owner_key=key,resource_owner_secret=secret)
        hdr = getAuthHeaders(androidBearer)
        del hdr["Authorization"]
        hdr["X-Twitter-Client"] = "TwitterAndroid"

        uri, headers, body = twt.sign(url, headers=hdr,realm="http://api.twitter.com/")

        response = requests.get(url,headers=headers)
    else:
        if btoken is None:
            return cycleBearerTokenGet(url,getAuthHeaders(bearer,authToken=authToken,guestToken=guestToken))
        headers = getAuthHeaders(btoken,authToken=authToken,guestToken=guestToken)
        response = requests.get(url, headers=headers)

    return response

def getAuthHeaders(btoken,authToken=None,guestToken=None):
    csrfToken=str(uuid.uuid4()).replace('-', '')
    headers = {"x-twitter-active-user":"yes","x-twitter-client-language":"en","x-csrf-token":csrfToken,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}
    headers['Authorization'] = btoken

    if authToken is not None:
        headers["Cookie"] = f"auth_token={authToken}; ct0={csrfToken}; "
        headers["x-twitter-auth-type"] = "OAuth2Session"
    if guestToken is not None:
        headers["x-guest-token"] = guestToken

    return headers

def getGuestToken():
    global guestToken
    global guestTokenUses
    if guestToken is None:
        r = requests.get(f"https://{twitterUrl}",headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0","Cookie":"night_mode=2"},allow_redirects=False)
        m = re.search(gt_pattern, r.text)
        if m is None:
            r = requests.post(f"https://api.{twitterUrl}/1.1/guest/activate.json", headers={"Authorization":bearer})
            guestToken = json.loads(r.text)["guest_token"]
        else:
            guestToken = m.group(1)
        guestTokenUses = 0
    else:
        guestTokenUses+=1
        if guestTokenUses > 40:
            gtTemp = guestToken
            guestToken = None
            guestTokenUses = 0
            return gtTemp
    return guestToken

def extractStatus_token(url,workaroundTokens):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error")
    twid = m.group(2)
    if workaroundTokens == None:
        raise TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = workaroundTokens
    random.shuffle(tokens)
    for authToken in tokens:
        try:

            tweet = requests.get(f"https://api.{twitterUrl}/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers=getAuthHeaders(bearer,authToken=authToken))
            output = tweet.json()
            if "errors" in output:
                # try another token
                continue
        except Exception as e:
            continue
        return output
    raise TwExtractError(400, "Extract error")

def extractStatus_guestToken(url):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        return extractStatus_token(url)
    twid = m.group(2)
    # get guest token
    guestToken = getGuestToken()
    # get tweet
    tweet = requests.get(f"https://api.{twitterUrl}/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers={"Authorization":bearer, "x-guest-token":guestToken})
    output = tweet.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        raise TwExtractError(error["code"], error["message"])
    return output

digits = "0123456789abcdefghijklmnopqrstuvwxyz"

def baseConversion(x, base):
    result = ''
    i = int(x)
    while i > 0:
        result = digits[i % base] + result
        i = i // base
    if int(x) != x:
        result += '.'
        i = x - int(x)
        d = 0
        while i != int(i):
            result += digits[int(i * base % base)]
            i = i * base
            d += 1
            if d >= 8:
                break
    return result

def calcSyndicationToken(idStr):
    id = int(idStr) / 1000000000000000 * math.pi
    o = baseConversion(x=id, base=int(math.pow(6, 2)))
    c = o.replace('0', '').replace('.', '')
    if c == '':
        c = '0'
    return c

def extractStatus_syndication(url,workaroundTokens=None):
    # https://github.com/mikf/gallery-dl/blob/46cae04aa3a113c7b6bbee1bb468669564b14ae8/gallery_dl/extractor/twitter.py#L1784
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error")
    twid = m.group(2)
    tweet = requests.get("https://cdn.syndication.twimg.com/tweet-result?id=" + twid+"&token="+calcSyndicationToken(twid))


    if tweet.status_code == 404:
        raise TwExtractError(404, "Tweet not found")
    output = tweet.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        raise TwExtractError(error["code"], error["message"])

    # change returned data to match the one from the other methods
    output['full_text'] = output['text']
    output['user']['profile_image_url'] = output['user']['profile_image_url_https']
    output['retweet_count']=0
    if 'mediaDetails' in output:
        output['extended_entities'] = {'media':output['mediaDetails']}
        for media in output['extended_entities']['media']:
            media['media_url'] = media['media_url_https']
    if 'quoted_tweet' in output:
        output['quoted_status'] = output['quoted_tweet']
        quotedID=output['quoted_tweet']['id_str']
        quotedScreenName=output['quoted_tweet']['user']['screen_name']
        output['quoted_status_permalink'] = {'expanded':f"https://{twitterUrl}/{quotedScreenName}/status/{quotedID}"}

    #output['user']['']

    return output

def extractStatus_twExtractProxy(url,workaroundTokens=None):
    proxies = os.getenv("VXTWITTER_PROXIES",None)
    if proxies is None:
        raise TwExtractError(400, "Extract error")
    proxies = proxies.split(',')
    random.shuffle(proxies)
    for proxy in proxies:
        try:
            tweet = requests.get(f"{proxy}?url={urllib.parse.quote(url)}")
            output = tweet.json()
            if "errors" in output:
                # try another token
                continue
        except Exception as e:
            continue
        return output

def extractStatusV2(url,workaroundTokens):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error (url not valid)")
    twid = m.group(2)
    if workaroundTokens == None:
        raise TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = workaroundTokens
    random.shuffle(tokens)
    for authToken in tokens:
        try:
            vars = json.loads('{"includeTweetImpression":true,"includeHasBirdwatchNotes":false,"includeEditPerspective":false,"rest_ids":["x"],"includeEditControl":true,"includeCommunityTweetRelationship":true,"includeTweetVisibilityNudge":true}')
            vars['rest_ids'][0] = str(twid)
            tweet = twitterApiGet(f"https://x.com/i/api/graphql/{v2graphql_api}/TweetResultsByIdsQuery?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(v2Features)}",authToken=authToken)
            try:
                rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
                print(f"Twitter Token Rate limit remaining: {rateLimitRemaining}")
            except: # for some reason the header is not always present
                pass
            if tweet.status_code == 429:
                print("Rate limit reached for token (429)")
                # try another token
                continue
            output = tweet.json()

            if "errors" in output:
                print(f"Error in output: {json.dumps(output['errors'])}")
                # try another token
                continue
            entries=output['data']['tweet_results']
            tweetEntry=None
            for entry in entries:
                if 'result' not in entry:
                    print("Tweet result not found in entry")
                    continue
                result = entry['result']
                if '__typename' in result and result['__typename'] == 'TweetWithVisibilityResults':
                    result=result['tweet']
                elif '__typename' in result and result['__typename'] == 'TweetUnavailable':
                    if 'reason' in result:
                        return {'error':'Tweet unavailable: '+result['reason']}
                    return {'error':'Tweet unavailable'}
                if 'rest_id' in result and result['rest_id'] == twid:
                    tweetEntry=result
                    break
            tweet=tweetEntry
            if tweet is None:
                print("Tweet 404")
                return {'error':'Tweet not found (404); May be due to invalid tweet, changes in Twitter\'s API, or a protected account.'}
        except Exception as e:
            print(f"Exception in extractStatusV2: {str(e)}")
            continue
        return tweet
    raise TwExtractError(400, "Extract error")

def extractStatusV2Android(url,workaroundTokens):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error (url not valid)")
    twid = m.group(2)
    if workaroundTokens == None:
        raise TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = workaroundTokens
    random.shuffle(tokens)
    for authToken in tokens:
        try:

            vars = json.loads('{"referrer":"home","includeTweetImpression":true,"includeHasBirdwatchNotes":false,"isReaderMode":false,"includeEditPerspective":false,"includeEditControl":true,"focalTweetId":0,"includeCommunityTweetRelationship":true,"includeTweetVisibilityNudge":true}')
            vars['focalTweetId'] = int(twid)
            tweet = twitterApiGet(f"https://x.com/i/api/graphql/{androidGraphql_api}/ConversationTimelineV2?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(androidGraphqlFeatures)}", authToken=authToken)
            try:
                rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
                print(f"Twitter Android Token Rate limit remaining: {rateLimitRemaining}")
            except: # for some reason the header is not always present
                pass
            if tweet.status_code == 429:
                print("Rate limit reached for android token")
                # try another token
                continue
            output = tweet.json()

            if "errors" in output:
                print(f"Error in output: {json.dumps(output['errors'])}")
                # try another token
                continue
            entries=output['data']['timeline_response']['instructions'][0]['entries']
            tweetEntry=None
            for entry in entries:
                if 'content' not in entry:
                    print("Tweet content not found in entry")
                    continue
                if '__typename' not in entry['content'] or entry['content']['__typename'] != 'TimelineTimelineItem' or entry['content']['content']['__typename'] != 'TimelineTweet':
                    continue
                result = entry['content']['content']['tweetResult']['result']
                if '__typename' not in result or result['__typename'] != 'Tweet':
                    continue
                if 'rest_id' in result and result['rest_id'] == twid:
                    tweetEntry=result
                    break
            tweet=tweetEntry
            if tweet is None:
                print("Tweet 404")
                return {'error':'Tweet not found (404); May be due to invalid tweet, changes in Twitter\'s API, or a protected account.'}
        except Exception as e:
            print(f"Exception in extractStatusV2: {str(e)}")
            continue

        return tweet
    raise TwExtractError(400, "Extract error")

def extractStatusV2TweetDetail(url,workaroundTokens):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error (url not valid)")
    twid = m.group(2)
    if workaroundTokens == None:
        raise TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = workaroundTokens
    random.shuffle(tokens)
    for authToken in tokens:
        try:

            vars = json.loads('{"focalTweetId":"0","with_rux_injections":false,"includePromotedContent":true,"withCommunity":true,"withQuickPromoteEligibilityTweetFields":true,"withBirdwatchNotes":true,"withVoice":true,"withV2Timeline":true}')
            vars['focalTweetId'] = str(twid)
            tweet = twitterApiGet(f"https://x.com/i/api/graphql/{tweetDetailGraphql_api}/TweetDetail?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(tweetDetailGraphqlFeatures)}", authToken=authToken)
            try:
                rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
                print(f"Twitter Token Rate limit remaining: {rateLimitRemaining}")
            except: # for some reason the header is not always present
                pass
            if tweet.status_code == 429:
                print("Rate limit reached for token")
                # try another token
                continue
            output = tweet.json()

            if "errors" in output:
                print(f"Error in output: {json.dumps(output['errors'])}")
                # try another token
                continue
            entries=output['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
            tweetEntry=None
            for entry in entries:
                if 'content' not in entry:
                    print("Tweet content not found in entry")
                    continue
                if '__typename' not in entry['content'] or entry['content']['__typename'] != 'TimelineTimelineItem' or entry['content']['itemContent']['__typename'] != 'TimelineTweet':
                    continue
                result = entry['content']['itemContent']['tweet_results']['result']
                if '__typename' not in result or result['__typename'] != 'Tweet':
                    continue
                if 'rest_id' in result and result['rest_id'] == twid:
                    tweetEntry=result
                    break
            tweet=tweetEntry
            if tweet is None:
                print("Tweet 404")
                return {'error':'Tweet not found (404); May be due to invalid tweet, changes in Twitter\'s API, or a protected account.'}
        except Exception as e:
            print(f"Exception in extractStatusV2: {str(e)}")
            continue

        return tweet
    raise TwExtractError(400, "Extract error")

def extractStatusV2Anon(url,x):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise TwExtractError(400, "Extract error")
    twid = m.group(2)

    guestToken = getGuestToken()

    # get tweet
    try:
        vars = json.loads('{"tweetId":"0","withCommunity":false,"includePromotedContent":false,"withVoice":false}')
        vars['tweetId'] = str(twid)
        tweet = requests.get(f"https://x.com/i/api/graphql/{v2AnonGraphql_api}/TweetResultByRestId?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(v2AnonFeatures)}", headers=getAuthHeaders(v2bearer,guestToken=guestToken))
        try:
            rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
            print(f"Twitter Anon Token Rate limit remaining: {rateLimitRemaining}")
        except: # for some reason the header is not always present
            pass
        if tweet.status_code == 429:
            raise TwExtractError(400, "Extract error")
        output = tweet.json()

        if "errors" in output:
            raise TwExtractError(400, "Extract error")
        entry=output['data']['tweetResult']
        tweetEntry=None
        result = entry['result']
        if '__typename' in result and result['__typename'] == 'TweetWithVisibilityResults':
            result=result['tweet']
        elif '__typename' in result and result['__typename'] == 'TweetUnavailable':
            if 'reason' in result:
                raise TwExtractError(400, "Extract error: "+result['reason'])
            raise TwExtractError(400, "Extract error")
        if 'rest_id' in result and result['rest_id'] == twid:
            tweetEntry=result
        tweet=tweetEntry
    except Exception as e:
        raise TwExtractError(400, "Extract error")
    if 'card' in tweet and 'legacy' in tweet['card']:
        tweet['card'] = tweet['card']['legacy']
    return tweet

def fixTweetData(tweet):
    try:
        if 'user' not in tweet:
            tweet['user'] = tweet['core']['user_results']['result']['legacy']
    except:
        print("fixTweetData error: No user")
        pass

    try:
        if 'extended_entities' not in tweet and 'extended_entities' in tweet['legacy']:
            tweet['extended_entities'] = tweet['legacy']['extended_entities']
    except:
        print("fixTweetData error: extended_entities")
        pass
    return tweet

def extractStatus(url,workaroundTokens=None):
    methods=[extractStatusV2Anon,extractStatusV2TweetDetail,extractStatusV2Android,extractStatusV2]
    for method in methods:
        try:
            result = method(url,workaroundTokens)
            if 'legacy' not in result:
                print(f"{method.__name__} method failed: Legacy not found for {url}")
                # try another method
                continue
            return fixTweetData(result)
        except Exception as e:
            print(f"{method.__name__} method failed: {str(e)} for {url}")
            continue
    raise TwExtractError(400, "Extract error")

def extractUser(url,workaroundTokens):
    useId=True
    m = re.search(userIDregex, url)
    if m is None:
        m = re.search(userregex, url)
        if m is None:
            raise TwExtractError(400, "Invalid URL")
        else:
            useId=False
    screen_name = m.group(1)
    # get user
    tokens = workaroundTokens
    random.shuffle(tokens)
    for authToken in tokens:
        if authToken.startswith("oa|"): # oauth token not supported atm
            continue
        try:

            reqHeaders = getAuthHeaders(bearer,authToken=authToken)
            if not useId:
                user = requests.get(f"https://api.{twitterUrl}/1.1/users/show.json?screen_name={screen_name}",headers=reqHeaders)
            else:
                user = requests.get(f"https://api.{twitterUrl}/1.1/users/show.json?user_id={screen_name}",headers=reqHeaders)
            output = user.json()
            if "errors" in output:
                # pick the first error and create a twExtractError
                error = output["errors"][0]
                raise TwExtractError(error["code"], error["message"])
            return output
        except Exception as e:
            continue
    raise TwExtractError(400, "Extract error")

#def extractUserByID(id):


def lambda_handler(event, context):
    if ("queryStringParameters" not in event):
        return {
            "statusCode": 400,
            "body": "Invalid request."
        }
    url = event["queryStringParameters"].get("url","")
    return {
        'statusCode': 200,
        'body': extractStatus(url,workaroundTokens=os.getenv("VXTWITTER_WORKAROUND_TOKENS",None).split(','))
    }