from wtforms import Form, TextField, PasswordField, validators
from flask_wtf.file import FileRequired, FileAllowed, FileField

class LoginForm(Form):
    username = TextField('username', [validators.Length(min=4, max=25)])
    password = PasswordField('password', [
        validators.Required(),
    ])


class UploadForm(Form):
    dataset = FileField('dataset', validators=[
        FileRequired(),
        FileAllowed(['preproc'], '.preproc files only')
        ])
    title = TextField('Title', [validators.Length(min=4, max=25)])
