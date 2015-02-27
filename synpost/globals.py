__author__ = 'Blake'

# adding the variables as properties on a
# static class makes the variables static as well.
# this will prevent overwriting static assets by
# mistake. It also prevents a cleaner interface
# for segmenting Value imports if they become
# too numerous
class Values(object):
    pass

Values.JINJA_ADDITIONAL_FOLDERS = ['pages']
Values.JINJA_CACHE_FILES = 500
Values.DEFAULT_INDEX_HTML = '''
<html>
    <head>
        <title>Generated by Synpost</title>
    </head>
    <body>
        <h1>Hi!</h1>
        This page was automatically generated by Synpost!
        <br>
        See, https://github.com/blakev/synpost for help on getting started :)
        <br>
        <hr>
    </body>
</html>
'''