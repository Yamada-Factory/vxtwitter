from weakref import finalize
from flask import Flask, render_template, request, redirect, abort, Response, send_from_directory, url_for, send_file, make_response, jsonify
from flask_cors import CORS
import re
import os
import combineImg
from io import BytesIO, StringIO
import urllib
import msgs
import twExtract as twExtract
from configHandler import config
from cache import addVnfToLinkCache,getVnfFromLinkCache
from yt_dlp.utils import ExtractorError
import vxlogging as log
from utils import getTweetIdFromUrl, pathregex
from vxApi import getApiResponse
from urllib.parse import urlparse
from PyRTF.Elements import Document
from PyRTF.document.section import Section
from PyRTF.document.paragraph import Paragraph
from utils import BytesIOWrapper
from copy import deepcopy
app = Flask(__name__)
CORS(app)
user_agent=""

staticFiles = { # TODO: Use flask static files instead of this
    "favicon.ico": {"mime": "image/vnd.microsoft.icon","path": "favicon.ico"},
    "apple-touch-icon.png": {"mime": "image/png","path": "apple-touch-icon.png"},
    "openInApp.js": {"mime": "text/javascript","path": "openInApp.js"},
    "preferences": {"mime": "text/html","path": "preferences.html"},
    "style.css": {"mime": "text/css","path": "style.css"},
    "Roboto-Regular.ttf": {"mime": "font/ttf","path": "Roboto-Regular.ttf"},
}

generate_embed_user_agents = [
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/1596241936; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0",
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam FriendsUI Tenfoot/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
    "TelegramBot (like TwitterBot)",
    "Mozilla/5.0 (compatible; January/1.0; +https://gitlab.insrt.uk/revolt/january)",
    "Synapse (bot; +https://github.com/matrix-org/synapse)",
    "Iframely/1.3.1 (+https://iframely.com/docs/about)",
    "test"]

def isValidUserAgent(user_agent):
    return True
    if user_agent in generate_embed_user_agents:
        return True
    elif "WhatsApp/" in user_agent:
        return True
    return False

def fixMedia(mediaInfo):
    # This is for the iOS Discord app, which has issues when serving URLs ending in .mp4 (https://github.com/dylanpdx/BetterTwitFix/issues/210)
    if 'video.twimg.com' not in mediaInfo['url'] or 'convert?url=' in mediaInfo['url']:
        return mediaInfo
    mediaInfo['url'] = mediaInfo['url'].replace("https://video.twimg.com",f"{config['config']['url']}/tvid").replace(".mp4","")
    return mediaInfo

def message(text):
    return render_template(
        'default.html',
        message = text,
        color   = config['config']['color'],
        appname = config['config']['appname'],
        repo    = config['config']['repo'],
        url     = config['config']['url'] )

def renderImageTweetEmbed(tweetData,image,appnameSuffix=""):
    qrt = tweetData['qrt']
    embedDesc = msgs.formatEmbedDesc("Image",tweetData['text'],qrt,tweetData['pollData'])

    if image.startswith("https://pbs.twimg.com") and "?" not in image:
        image = f"{image}?name=orig"

    return render_template("image.html",
                    tweet=tweetData,
                    pic=[image],
                    host=config['config']['url'],
                    desc=embedDesc,
                    urlEncodedDesc=urllib.parse.quote(embedDesc),
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=msgs.formatProvider(config['config']['appname']+appnameSuffix,tweetData),
                    color=config['config']['color']
                    )

def renderVideoTweetEmbed(tweetData,mediaInfo,appnameSuffix=""):
    qrt = tweetData['qrt']
    embedDesc = msgs.formatEmbedDesc("Video",tweetData['text'],qrt,tweetData['pollData'])

    mediaInfo=fixMedia(mediaInfo)
    return render_template("video.html",
                    tweet=tweetData,
                    media=mediaInfo,
                    host=config['config']['url'],
                    desc=embedDesc,
                    urlEncodedDesc=urllib.parse.quote(embedDesc),
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=msgs.formatProvider(config['config']['appname']+appnameSuffix,tweetData),
                    color=config['config']['color']
                    )

def renderTextTweetEmbed(tweetData,appnameSuffix=""):
    qrt = tweetData['qrt']
    embedDesc = msgs.formatEmbedDesc("Text",tweetData['text'],qrt,tweetData['pollData'])
    return render_template("text.html",
                    tweet=tweetData,
                    host=config['config']['url'],
                    desc=embedDesc,
                    urlEncodedDesc=urllib.parse.quote(embedDesc),
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=msgs.formatProvider(config['config']['appname']+appnameSuffix,tweetData),
                    color=config['config']['color']
                    )

def renderArticleTweetEmbed(tweetData,appnameSuffix=""):
    articlePreview=tweetData['article']["title"]+"\n\n"+tweetData['article']["preview_text"]+"…"
    embedDesc = msgs.formatEmbedDesc("Image",articlePreview,None,None)
    return render_template("image.html",
                    tweet=tweetData,
                    pic=[tweetData['article']["image"]],
                    host=config['config']['url'],
                    desc=embedDesc,
                    urlEncodedDesc=urllib.parse.quote(embedDesc),
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=msgs.formatProvider(config['config']['appname']+appnameSuffix,tweetData),
                    color=config['config']['color']
                    )

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /"

@app.route('/') # If the useragent is discord, return the embed, if not, redirect to configured repo directly
def default():
    return redirect(config['config']['repo'], 301)

@app.route('/oembed.json') #oEmbed endpoint
def oembedend():
    desc  = request.args.get("desc", None)
    user  = request.args.get("user", None)
    link  = request.args.get("link", None)
    ttype = request.args.get("ttype", None)
    provName = request.args.get("provider",None)
    return  oEmbedGen(desc, user, link, ttype,providerName=provName)

def getTweetData(twitter_url,include_txt="false",include_rtf="false"):
    cachedVNF = getVnfFromLinkCache(twitter_url)
    if cachedVNF is not None and include_txt == "false" and include_rtf == "false":
        return cachedVNF

    try:
        rawTweetData = twExtract.extractStatusV2Anon(twitter_url)
    except:
        rawTweetData = None
    if rawTweetData is None:
        try:
            rawTweetData = twExtract.extractStatus(twitter_url,workaroundTokens=config['config']['workaroundTokens'].split(','))
        except:
            rawTweetData = None
    if rawTweetData == None or 'error' in rawTweetData:
        return None

    if rawTweetData is None:
        return None
    tweetData = getApiResponse(rawTweetData,include_txt,include_rtf)
    if tweetData is None:
        return None
    if include_txt == "false" and include_rtf == "false":
        addVnfToLinkCache(twitter_url,tweetData)
    return tweetData

def determineEmbedTweet(tweetData):
    # Determine which tweet, i.e main or QRT, to embed the media from.
    # if there is no QRT, return the main tweet => default behavior
    # if both don't have media, return the main tweet => embedding qrt text will be handled in the embed description
    # if both have media, return the main tweet => priority is given to the main tweet's media
    # if only the QRT has media, return the QRT => show the QRT's media, not the main tweet's
    # if only the main tweet has media, return the main tweet => show the main tweet's media, embedding QRT text will be handled in the embed description
    if tweetData['qrt'] is None:
        return tweetData
    if tweetData['qrt']['hasMedia'] and not tweetData['hasMedia']:
        return tweetData['qrt']
    return tweetData

@app.route('/<path:sub_path>') # Default endpoint used by everything
def twitfix(sub_path):
    if sub_path in staticFiles:
        if 'path' not in staticFiles[sub_path] or staticFiles[sub_path]["path"] == None:
            staticFiles[sub_path]["path"] = sub_path
        return send_from_directory(os.path.join(app.root_path, 'static'), staticFiles[sub_path]["path"], mimetype=staticFiles[sub_path]["mime"])
    if sub_path.startswith("status/"): # support for /status/1234567890 URLs
        sub_path = "i/" + sub_path
    match = pathregex.search(sub_path)
    if match is None:
        abort(404)
    twitter_url = f'https://twitter.com/i/status/{getTweetIdFromUrl(sub_path)}'
    # isApiRequest=request.url.startswith("https://api.vx") or request.url.startswith("http://api.vx")
    isApiRequest = True

    include_txt="false"
    include_rtf="false"

    if isApiRequest:
        if "include_txt" in request.args:
            include_txt = request.args.get("include_txt")
        if "include_rtf" in request.args:
            include_rtf = request.args.get("include_rtf")

    tweetData = getTweetData(twitter_url,include_txt,include_rtf)
    if tweetData is None:
        log.error("Tweet Data Get failed for "+twitter_url)
        return message(msgs.failedToScan)
    qrt = None
    if 'qrtURL' in tweetData and tweetData['qrtURL'] is not None:
        qrt = getTweetData(tweetData['qrtURL'])
    tweetData['qrt'] = qrt
    tweetData = deepcopy(tweetData)
    log.success("Tweet Data Get success")
    if '?' in request.url:
        requestUrlWithoutQuery = request.url.split("?")[0]
    else:
        requestUrlWithoutQuery = request.url

    directEmbed=False
    if requestUrlWithoutQuery.startswith("https://d.vx") or requestUrlWithoutQuery.endswith(".mp4") or requestUrlWithoutQuery.endswith(".png"):
        directEmbed = True
        # remove the .mp4 from the end of the URL
        if requestUrlWithoutQuery.endswith(".mp4") or requestUrlWithoutQuery.endswith(".png"):
            sub_path = sub_path[:-4]
    elif requestUrlWithoutQuery.endswith(".txt"):
        return Response(tweetData['text'], mimetype='text/plain')
    elif requestUrlWithoutQuery.endswith(".rtf"):
        doc = Document()
        section = Section()
        doc.Sections.append(section)
        p = Paragraph()
        p.append(tweetData['text'])
        section.append(p)
        rtf = StringIO()
        doc.write(rtf)
        rtf.seek(0)
        return send_file(BytesIOWrapper(rtf), mimetype='application/rtf', as_attachment=True, download_name=f'{tweetData["user_screen_name"]}_{tweetData["tweetID"]}.rtf')

    embedIndex = -1
    # if url ends with /1, /2, /3, or /4, we'll use that as the index
    if sub_path[-2:] in ["/1","/2","/3","/4"]:
        embedIndex = int(sub_path[-1])-1
        sub_path = sub_path[:-2]

    if isApiRequest: # Directly return the API response if the request is from the API
        return tweetData
    elif directEmbed: # direct embed
        # direct embeds should always prioritize the main tweet, so don't check for qrt
        # determine what type of media we're dealing with
        if not tweetData['hasMedia'] and qrt is None:
            return renderTextTweetEmbed(tweetData)
        elif tweetData['allSameType'] and tweetData['media_extended'][0]['type'] == "image" and embedIndex == -1 and tweetData['combinedMediaUrl'] != None:
            return render_template("rawimage.html",media={"url":tweetData['combinedMediaUrl']})
        else:
            # this means we have mixed media or video, and we're only going to embed one
            if embedIndex == -1: # if the user didn't specify an index, we'll just use the first one
                embedIndex = 0
            media = tweetData['media_extended'][embedIndex]
            media=fixMedia(media)
            if media['type'] == "image":
                return render_template("rawimage.html",media=media)
            elif media['type'] == "video" or media['type'] == "gif":
                return render_template("rawvideo.html",media=media)
    else: # full embed
        embedTweetData = determineEmbedTweet(tweetData)
        if "article" in embedTweetData and embedTweetData["article"] is not None:
            return renderArticleTweetEmbed(tweetData," - See original tweet for full article")
        elif not embedTweetData['hasMedia']:
            return renderTextTweetEmbed(tweetData)
        elif embedTweetData['allSameType'] and embedTweetData['media_extended'][0]['type'] == "image" and embedIndex == -1 and embedTweetData['combinedMediaUrl'] != None:
            return renderImageTweetEmbed(tweetData,embedTweetData['combinedMediaUrl'],appnameSuffix=" - See original tweet for full quality")
        else:
            # this means we have mixed media or video, and we're only going to embed one
            if embedIndex == -1: # if the user didn't specify an index, we'll just use the first one
                embedIndex = 0
            media = embedTweetData['media_extended'][embedIndex]
            if len(embedTweetData["media_extended"]) > 1:
                suffix = f' - Media {embedIndex+1}/{len(embedTweetData["media_extended"])}'
            else:
                suffix = ''
            if media['type'] == "image":
                return renderImageTweetEmbed(tweetData,media['url'] , appnameSuffix=suffix)
            elif media['type'] == "video" or media['type'] == "gif":
                if media['type'] == "gif":
                    if config['config']['gifConvertAPI'] != "" and config['config']['gifConvertAPI'] != "none":
                        vurl=media['originalUrl'] if 'originalUrl' in media else media['url']
                        media['url'] = config['config']['gifConvertAPI'] + "/convert?url=" + vurl
                        suffix += " - GIF"
                return renderVideoTweetEmbed(tweetData,media,appnameSuffix=suffix)

    return message(msgs.failedToScan)



@app.route('/tvid/<path:vid_path>')
def tvid(vid_path):
    url = f"https://video.twimg.com/{vid_path}.mp4"
    return redirect(url, 302)

@app.route("/rendercombined.jpg")
def rendercombined():
    # get "imgs" from request arguments
    imgs = request.args.get("imgs", "")

    if 'combination_method' in config['config'] and config['config']['combination_method'] != "local":
        url = config['config']['combination_method'] + "/rendercombined.jpg?imgs=" + imgs
        return redirect(url, 302)
    # Redirecting here instead of setting the embed URL directly to this because if the config combination_method changes in the future, old URLs will still work

    imgs = imgs.split(",")
    if (len(imgs) == 0 or len(imgs)>4):
        abort(400)
    #check that each image starts with "https://pbs.twimg.com"
    for img in imgs:
        result = urlparse(img)
        if result.hostname != "pbs.twimg.com" or result.scheme != "https":
            abort(400)
    finalImg= combineImg.genImageFromURL(imgs)
    imgIo = BytesIO()
    finalImg = finalImg.convert("RGB")
    finalImg.save(imgIo, 'JPEG',quality=70)
    imgIo.seek(0)
    return send_file(imgIo, mimetype='image/jpeg',max_age=86400)

def oEmbedGen(description, user, video_link, ttype,providerName=None):
    if providerName == None:
        providerName = config['config']['appname']
    out = {
            "type"          : ttype,
            "version"       : "1.0",
            "provider_name" : providerName,
            "provider_url"  : config['config']['repo'],
            "title"         : description,
            "author_name"   : user,
            "author_url"    : video_link
            }

    return out

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0')
