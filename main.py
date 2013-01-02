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


def http_get( url ,args):
    args = urllib.urlencode(args)
    if url.find('?') == -1 :
        url = '%s?%s'%(url,args)
    else:
        url = '%s&%s'%(url,args)
    request = urllib2.Request( url, args )
    request.add_header('Referer', url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
    response = urllib2.urlopen(request)
    return response


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class RequestHandler(webapp2.RequestHandler):
    def get(self):
        reqtype = self.request.get('reqtype')
        url = self.request.get('requrl')
        args = dict(self.request.params)
        
        if args.has_key('requrl'):
            args.pop('requrl')
        if args.has_key('reqtype'):
            args.pop('reqtype')
        response = http_get( url, args)
        if reqtype == 'xml' :
            self.response.headers["Content-Type"] = "text/xml"
        else:
            self.response.headers["Content-Type"] = "text/html"
        self.response.write(response.read())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/request', RequestHandler)
], debug=True)
