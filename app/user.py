class User(object):
  
  @staticmethod
  def get(userid):
    return User(userid)
  
  
  def __init__(self, userid):
    self.username = userid
  
  def make_admin(self):
    self.admin = True
  
  def is_authenticated(self):
    """Returns True if the user is authenticated, i.e. they have provided valid credentials.
  (Only authenticated users will fulfill the criteria of login_required.)"""
    return True
  def is_active(self):
    """Returns True if this is an active user - in addition to being authenticated, they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accounts may not log in (without being forced of course)."""
    return True
  def is_anonymous(self):
    """Returns True if this is an anonymous user. (Actual users should return False instead.)"""
    return False
  def get_id(self):
    """Returns a unicode that uniquely identifies this user, and can be used to load the user from the user_loader callback. Note that this must be a unicode - if the ID is natively an int or some other type, you will need to convert it to unicode."""
    return unicode(self.username)

    
