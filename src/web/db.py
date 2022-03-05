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
DB = pymongo.MongoClient(os.getenv('MONGO_URL', 'mongodb://db:27017/'),
                         username=os.getenv('MONGO_USERNAME'),
                         password=os.getenv('MONGO_PASSWORD'))

def _get_posts_col():
    return DB[DB_NAME]["posts"]


def save_post(post_data):
    """Save a new post or apply changes to existing post"""
    col = _get_posts_col()
    if '_id' in post_data:
        logger.debug('Found existing entry with id %s', post_data['_id'])
        col.replace_one({'_id': post_data['_id']}, post_data)
        return post_data['_id']
    else:
        res = col.insert_one(post_data)
        logger.debug('Created a new entry %s', res)
        return res.inserted_id


def get_post(post_id):
    """Retrieve post by id"""
    col = _get_posts_col()
    res = col.find_one({"_id": bson.ObjectId(post_id)})
    return res


def get_all_posts(criteria=None, date_format=None):
    """
    Retrieve posts matching the criteria if one is specified.
    If date_format is passed, the date will be converted to expected format and returned as string.
    """
    logger.debug('Preparing to get all posts')
    col = _get_posts_col()
    res = list(col.find() if criteria is None else col.find(criteria))
    # apply date formatting
    if date_format is not None:
        for r in res:
            try:
                r['date'] = r.get('date').strftime(date_format)
            except (KeyError, AttributeError):
                r['date'] = ''
    return res


def delete_post(post_id):
    """Delete post by id"""
    col = _get_posts_col()
    col.delete_one({"_id": bson.ObjectId(post_id)})
