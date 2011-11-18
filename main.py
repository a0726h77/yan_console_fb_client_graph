# coding:utf-8

#
# A comand line fasebook publisher
#

import os
import optparse
import urllib
import urllib2
#import sys
import re
from configobj import ConfigObj
#import time
import simplejson

class myFB():
    def __init__(self):
        config_file = os.path.join( os.getenv('HOME'), ".yan_console_f_b_client.cfg" )
        config = ConfigObj(config_file)
        email = config['fb_user']
        passwd = config['fb_pass']

        # build opener with HTTPCookieProcessor
        self.opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
        urllib2.install_opener( self.opener )

        print 'Login ...'
        self.form_id = self.login(email, passwd)
        
        print 'Get token ...'
        self.token = self.getToken()

    def login(self, email, passwd):
        #login_url = 'https://login.facebook.com/login.php?m=m&refsrc=http://m.facebook.com/index.php&fbb=rd88e1687&refid=8'
        #login_url = 'https://login.facebook.com/'
        login_url = 'https://www.facebook.com/login.php?m=m&refsrc=http%3A%2F%2Fm.facebook.com%2F&refid=8'
        loginRequest = urllib2.Request ( login_url , 'email=%s&pass=%s&login=Log+In' % (email, passwd))
        urllib2.urlopen (loginRequest)                                                 
        connection = urllib2.urlopen ('https://m.facebook.com/')                        
        form_id = re.findall ('name="post_form_id" value="(\w+)"', connection.read ())[0]

        print 'Get form id : %s' % form_id

        return form_id 

    def getToken(self):
        print 'Access token : ',

        request = urllib2.Request('https://www.facebook.com/dialog/oauth?client_id=120190928021712&redirect_uri=http://www.facebook.com/connect/login_success.html&response_type=token')
        connection = urllib2.urlopen (request)
        #time.sleep(2)
        connection.read()

	url = connection.url
        #print url
        p = re.compile('access_token=([a-zA-Z0-9]+)&')
        token = p.findall(url)[0]
        print token

        return token

    def getUID(self):
        url = 'https://graph.facebook.com/me?access_token=%s&fields=%s' % (self.token, 'id')
        connection = urllib2.urlopen(url)
        uid = connection.read()
    
        return simplejson.loads(uid)['id']

    def statusCreate(self, uid, message):
        form_fields = {
           "access_token" : self.token,
           "message" : message,
        }
        form_data = urllib.urlencode(form_fields)

        # bellow code to encode POST arguments to unicode, but my environment just utf8
        #temp = {}
        #for k, v in form_fields.iteritems():
        #    temp[k] = unicode(v).encode('utf-8')
        #form_data = urllib.urlencode(temp)
    
        url = 'https://graph.facebook.com/%s/feed' % uid
        request = urllib2.Request(url ,form_data)
        connection = urllib2.urlopen(request)

        return connection.read()

if __name__ == "__main__":
    p = optparse.OptionParser(description="A comand line fasebook publisher", prog="main")
    p.add_option("--get-uid", action="store_true", default=False, help="Get the user's Facebook ID")
    p.add_option("--status", metavar="MESSAGE", dest="status_message", help="post a status message on behalf of the user")
    p.add_option("--id", metavar="ID", dest="uid", help="Set the ID for operation. If not assigned, ID = me")
    (options, args) = p.parse_args()
    #print args, options

    if options.get_uid:
        fb = myFB()
        print fb.getUID()
    elif options.status_message:
        fb = myFB()
        if options.uid:
            uid = options.uid
        else:
            uid = fb.getUID()
        print fb.statusCreate(uid, options.status_message)
    else:
        p.parse_args(['-h'])

