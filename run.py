# -*- coding:utf-8 -*-  
import sys
import os, time
from flask import Flask,g,request,make_response,render_template
import hashlib
import xml.etree.ElementTree as ET
import json, requests
import jieba

def fenci(word):
    seg_list = jieba.cut(word,cut_all=False)
    return "/ ".join(seg_list) 

def youdao(word):
    word = word.encode('utf-8')
    params = {
        'keyfrom':'tigerisnotinwood',
        'key':'1195684388',
        'type':'data',
        'doctype':'json',
        'version':'1.1',
        'q':word
    }
    url = 'http://fanyi.youdao.com/openapi.do'
    
    try:
        resp = requests.get(url, params, timeout = 2)
    except requests.exceptions.Timeout:
        return u"Time Out"
    
    print resp.text

    fanyi = json.loads(resp.text)
    if fanyi['errorCode'] == 0:        
        if 'basic' in fanyi.keys():
            trans = u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join(fanyi['web'][0]['value']))
            return trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
            return trans
    elif fanyi['errorCode'] == 20:
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] == 30:
        return u'对不起，无法进行有效的翻译'
    elif fanyi['errorCode'] == 40:
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'% word

app = Flask(__name__)
app.debug=True

@app.route('/',methods=['GET','POST'])
def wechat_auth():
    if request.method == 'GET':
        token='zhou'
        data = request.args
        signature = data.get('signature','')
        timestamp = data.get('timestamp','')
        nonce = data.get('nonce','')
        echostr = data.get('echostr','')
        s = [timestamp,nonce,token]
        s.sort()
        s = ''.join(s)
        if (hashlib.sha1(s).hexdigest() == signature):
            return make_response(echostr)
    else:
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)
        tou = xml_rec.find('ToUserName').text
        fromu = xml_rec.find('FromUserName').text
        content = xml_rec.find('Content').text
        print content
        
        fanyi = youdao(content)
        
        res = render_template('msg.xml', 
            toUserName   = fromu,
            fromUserName = tou,
            createTime   = str(int(time.time())),
            content      = fanyi)
            
        return res

app.run(host = os.getenv('IP','0.0.0.0'), port=int(os.getenv('PORT',8080)))


