#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import urllib
import urllib2
from google.appengine.api import urlfetch
from bs4 import BeautifulSoup
#import BeautifulSoup

def getBaseUri(uri):
    idx = uri.rfind('/')
    pidx = uri.find('://')
    if idx == -1 :
        return uri
    if idx == pidx+2 :
        return uri
    return uri[:idx]


def getTopUri(uri):
    pidx = uri.find('://')
    uri2 = uri[pidx+3:]
    idx = uri2.find('/')
    if idx == -1 :
        return uri
    return '%s%s'%(uri[:pidx+3],uri2[:idx])


def convertURL(origin, url):
    soup = BeautifulSoup(origin)
    #soup = BeautifulSoup.BeautifulSoup(origin)
    links = soup.findAll(attrs={'href':True})
    for link in links :
        if link['href'].startswith('http') :
            link['href'] = '/?rq=%s'%(link['href'])
        elif link['href'].startswith('/'):
            link['href'] = '/?rq=%s%s'%(getTopUri(url),link['href'])
        else:
            link['href'] = '/?rq=%s/%s'%(getBaseUri(url),link['href'])

    tags = soup.findAll(attrs={'src':True})
    originURL = url
    for tag in tags :
        if tag['src'].startswith('http') :
            tag['src'] = '/?rq=%s'%(tag['src'])
        #elif tag['src'].startswith('./'):
        #    t = tag['src'].replace('./','')
        #    tag['src'] = '/?rq=%s/%s'%(getBaseUri(url),t)
        elif tag['src'].startswith('/'):
            tag['src'] = '/?rq=%s%s'%(getTopUri(url),tag['src'])
        else:
            tag['src'] = '/?rq=%s/%s'%(getBaseUri(url),tag['src'])

    tags = soup.findAll(attrs={'action':True})
    for tag in tags :
        if tag['action'].startswith('http') :
            tag['action'] = '/?rq=%s'%(tag['action'])
        elif tag['action'].startswith('/'):
            tag['action'] = '/?rq=%s%s'%(getTopUri(url),tag['action'])
        else:
            tag['action'] = '/?rq=%s/%s'%(getBaseUri(url),tag['action'])
    return soup.renderContents()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('rq')
        if not url :
            self.response.write('URL:<form action=/><input type=text name=rq value=http://></form>')
            return

        args = dict(self.request.params)
        if args.has_key('rq'):
            args.pop('rq')
        args = urllib.urlencode(args)
        if len(args) > 0 :
            if url.find('?') == -1 :
                url = '%s?%s'%(url,args)
            else:
                url = '%s&%s'%(url,args)

        response = urlfetch.fetch(url=url, 
                                  method=urlfetch.GET,
                                  headers=self.request.headers)
        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return
        self.response.write(convertURL(response.content,url))

    def post(self):
        url = self.request.get('rq')
        if not url :
            self.response.write('Hello world!')

        args = dict(self.request.params)
        if args.has_key('rq'):
            args.pop('rq')
        args = urllib.urlencode(args)
        response = urlfetch.fetch(url=url, 
                                  payload=args,
                                  method=urlfetch.POST,
                                  headers=self.request.headers)
        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return
        self.response.write(convertURL(response.content,url))


class proxyHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('rq')
        args = dict(self.request.params)
        if args.has_key('rq'):
            args.pop('rq')
        args = urllib.urlencode(args)
        if url.find('?') == -1 :
            url = '%s?%s'%(url,args)
        else:
            url = '%s&%s'%(url,args)

        response = urlfetch.fetch(url=url, 
                                  method=urlfetch.GET,
                                  headers=self.request.headers)

        self.response.headers = response.headers
        self.response.write(response.content)

    def post(self):
        url = self.request.get('rq')
        args = dict(self.request.params)
        if args.has_key('rq'):
            args.pop('rq')
        args = urllib.urlencode(args)
        response = urlfetch.fetch(url=url, 
                                  payload=args, 
                                  method=urlfetch.POST,
                                  headers=self.request.headers)

        self.response.headers = response.headers
        self.response.write(response.content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/r', proxyHandler)
], debug=True)
