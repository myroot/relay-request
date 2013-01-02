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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

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
