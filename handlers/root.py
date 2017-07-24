#!/usr/bin/python
#


import logging
from cgi import parse_qs
from datetime import datetime
import re
import random
import os
import string
import urllib
from urlparse import urlparse
import json
import webapp2
from basehandler.basehandler import BaseHandler
from model.inbound_requests import InboundRequest
from google.appengine.api import taskqueue
import model.inbound_requests


REQUEST_ROW_TEMPLATE = '<table>' \
    '<tbody>' \
    '<tr>' \
    '<td>%s</td>' \
    '<td>%s</td>' \
    '<td>%s</td>' \
    '</tr>' \
    '</tbody>'\
    '</table>'

HEADER_BODY_ROW_TEMPLATE = '<table>' \
    '<tbody>' \
    '<tr>' \
    '<td>%s</td>' \
    '<td>%s</td>' \
    '</tr>' \
    '</tbody>'\
    '</table>'


class RootHandler(BaseHandler):
    """Handles search requests for comments."""

    def get(self):
        """Handles a get request with a query."""
        if 'wipe' in self.request.path_url:
            InboundRequest.wipe()
            self.response.write('Db wiped')
            return

        # log out last 10 requests
        data = InboundRequest.get_latest()

        resultList = []
        for item in data:
            headers = ''
            header_list = item.request_headers.split('\r\n')

            # try format if json
            body = item.request_body
            try:
                json_body = json.loads(item.request_body)
                body = json.dumps(json_body, indent=2, separators=(',', ': '))
            except:
                #logging.info('not in json')
                pass

            resultfields = {'ts':  item.time_stamp, 'host_url': item.request_host_url, 'path': item.request_path,
                            'query_params': item.request_query_params, 'headers': header_list, 'body': body}
            resultList.append(resultfields)

        template_values = {
            'number_returned': len(data),
            'results': resultList
        }
        self.render_template('index.html', template_values)

    def post(self):
        """Handles a get request with a query."""

        headers = ''
        for key, value in self.request.headers.iteritems():
            headers += '%s: %s' % (key, value)
            headers += '\r\n'
        InboundRequest.add_record(datetime.utcnow(), self.request.host_url,
                                  self.request.path, headers, self.request.query_string, self.request.body)

        taskqueue.add(url='/check_wipe_task')


class CheckWiperTaskHandler(BaseHandler):

    def post(self):
        InboundRequest.wipe_if_big()


logging.getLogger().setLevel(logging.DEBUG)

application = webapp2.WSGIApplication([
    ('/check_wipe_task', CheckWiperTaskHandler),
    ('/.*', RootHandler)

],
    debug=True)
