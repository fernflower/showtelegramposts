"""Database interface to be used in web and bot"""
import bson
import logging
import os

import dotenv
import pymongo

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# load env vars from .env
# NOTE(ivasilev) The hardcoded path is because of issues with passing env vars in uwsgi.ini
dotenv.load_dotenv(os.getenv('DOT_ENV_FILE', '/app/.env'))

DB_NAME = 'posts'


def create_client():
    """
    Create an instance of MongoClient.
    Need to so that as pymongo is not fork safe, without this db connection won't be processed properly
    https://stackoverflow.com/questions/54778245/timeout-with-flask-uwsgi-nginx-app-using-mongodb
    """
    client = pymongo.MongoClient(os.getenv('MONGO_URL', 'mongodb://db:27017/'),
                                 username=os.getenv('MONGO_USERNAME'),
                                 password=os.getenv('MONGO_PASSWORD'), connect=False)
    return client


def _get_posts_col(client=None):
    client = client or create_client()
    return client[DB_NAME]["posts"]


def save_post(post_data, client=None):
    """Save a new post or apply changes to existing post"""
    col = _get_posts_col(client)
    if '_id' in post_data:
        logger.debug('Found existing entry with id %s', post_data['_id'])
        col.replace_one({'_id': post_data['_id']}, post_data)
        return post_data['_id']
    else:
        res = col.insert_one(post_data)
        logger.debug('Created a new entry %s', res)
        return res.inserted_id


def get_post(post_id, client=None):
    """Retrieve post by id"""
    col = _get_posts_col(client)
    res = col.find_one({"_id": bson.ObjectId(post_id)})
    return res


def get_all_posts(criteria=None, date_format=None, client=None):
    """
    Retrieve posts matching the criteria if one is specified.
    If date_format is passed, the date will be converted to expected format and returned as string.
    """
    logger.debug('Preparing to get all posts')
    col = _get_posts_col(client)
    res = list(col.find() if criteria is None else col.find(criteria))
    for r in res:
        # apply date formatting
        if date_format is not None:
            try:
                r['date'] = r.get('date').strftime(date_format)
            except (KeyError, AttributeError):
                r['date'] = ''
        # add <a> tag to links and strip excessive newlines
        text_with_paragraphs = ''
        for paragraph in r['text'].split('\n'):
            text_with_paragraphs += f'<p> {paragraph} </p>'
        text_with_links = ''
        for word in text_with_paragraphs.split(' '):
            if word.startswith('http://') or word.startswith('https://'):
                word = f'<a href="{word}" target="_blank">{word}</a>'
            text_with_links += f' {word}'
        r['text'] = text_with_links
    return res


def delete_post(post_id, client=None):
    """Delete post by id"""
    col = _get_posts_col(client)
    col.delete_one({"_id": bson.ObjectId(post_id)})
