import os
import codecs
import json

from flask.ext.login import UserMixin

from conf import *

class User(UserMixin):
    file_format_string = os.path.join(USER_DIR, '{}.json') 
 
    @staticmethod
    def get(userid):
        if not os.path.exists(User.file_format_string.format(userid)):
            return None
        return User(userid)

    @staticmethod
    def get_user_list():
        files = glob.glob(User.file_format_string.format('*')) 
        regex = User.file_format_string.format(r'(.*)\\')
        return [re.search(regex, path).group(1) for path in files]
   
    @staticmethod
    def check_password(userid, password):
        with codecs.open(User.file_format_string.format(userid), 'r', 'utf-8') as f:
            expected = json.loads(f.read())['password']
        if expected == password:
            return True
        return False
    
    def __init__(self, userid):
        self.username = userid
        self.filepath = os.path.join(User.file_format_string.format(userid))
        self.annoDic = None
  
    def make_admin(self):
        self.admin = True

    def is_admin(self):
        return True if self.username in ADMINS else False
  
    def is_authenticated(self):
        """Returns True if the user is authenticated, i.e. they have provided 
        valid credentials. (Only authenticated users will fulfill the criteria 
        of login_required.)"""
        return True

    def is_active(self):
        """Returns True if this is an active user - in addition to being 
        authenticated, they also have activated their account, not been 
        suspended, or any condition your application has for rejecting an 
        account. Inactive accounts may not log in (without being forced of 
        course)."""
        return True

    def is_anonymous(self):
        """Returns True if this is an anonymous user. (Actual users should 
        return False instead.)"""
        return False

    def get_id(self):
        """Returns a unicode that uniquely identifies this user, and can be 
        used to load the user from the user_loader callback. Note that this 
        must be a unicode - if the ID is natively an int or some other type, 
        you will need to convert it to unicode."""
        return unicode(self.username)

    def save(self, annoDic):
        with codecs.open(self.filepath, 'w', 'utf-8') as f:
            f.write(json.dumps(annoDic))

    def load(self):
        with codecs.open(self.filepath, 'r', 'utf-8') as f:
            self.annoDic = json.loads(f.read())
            self.annoDic['password'] = 'mordo' ########################################### fix this
            return self.annoDic

    def get_current_anno(self):
        if not self.annoDic:
            self.annoDic = self.load()
        return self.annoDic['current'] 

    def set_current_anno(self, dataset, batch):
        if not self.annoDic:
            self.annoDic = self.load()
        self.annoDic['current'] = (dataset, batch)
        self.save(self.annoDic)

