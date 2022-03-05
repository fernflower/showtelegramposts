import os
import pkg_resources

from bottle import Bottle, request, route, run, static_file
import jinja2

from web import db

DATE_FORMAT = '%d/%m/%Y %H:%M:%S'
VIEWS_DIR = pkg_resources.resource_filename('web', 'views')
STATIC_DIR = os.environ.get('STATIC_DIR', 'static')
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(VIEWS_DIR),
    extensions=['jinja2.ext.i18n']
)
app = Bottle()
# NOTE(ivasilev) PyMongo is not fork safe https://jira.mongodb.org/browse/PYTHON-1139
app.dbclient = db.create_client()

@app.route('/')
def _index():
    template = env.get_or_select_template('index.tpl')
    return template.render()


@app.route(r'/posts/<message_type:re:.*>')
def _show_messages(message_type):
    template = env.get_or_select_template('posts.tpl')
    posts = db.get_all_posts({'type': message_type}, date_format=DATE_FORMAT, client=app.dbclient)
    return template.render(posts=posts)


@app.route(r'/static/<filepath:re:.*\.(pdf|xml|css|js|ico)>')
def _files(filepath):
    return static_file(filepath, root=f'{STATIC_DIR}/')


if __name__ == '__main__':
    run(app, host='localhost', port=8080)
