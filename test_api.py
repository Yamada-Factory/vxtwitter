from vx_testdata import *
import twitfix,twExtract
from flask.testing import FlaskClient
client = FlaskClient(twitfix.app)

def test_api_include_txt():
    resp = client.get(testTextTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_txt=true",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert any(".txt" in i for i in jData["mediaURLs"])

def test_api_include_rtf():
    resp = client.get(testTextTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_rtf=true",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert any(".rtf" in i for i in jData["mediaURLs"])

def test_api_include_txt_nomedia():
    resp = client.get(testTextTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_txt=ifnomedia",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert any(".txt" in i for i in jData["mediaURLs"])

    resp = client.get(testMediaTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_txt=ifnomedia",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert not any(".txt" in i for i in jData["mediaURLs"])

def test_api_include_rtf_nomedia():
    resp = client.get(testTextTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_rtf=ifnomedia",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert any(".rtf" in i for i in jData["mediaURLs"])

    resp = client.get(testMediaTweet.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_rtf=ifnomedia",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert not any(".rtf" in i for i in jData["mediaURLs"])

def test_api_user():
    resp = client.get(testUser.replace("https://twitter.com","https://api.vxtwitter.com")+"?include_rtf=true",headers={"User-Agent":"test"})
    jData = resp.get_json()
    assert resp.status_code==200
    assert jData["screen_name"]=="jack"