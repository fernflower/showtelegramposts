"""Database interface to be used in web and bot"""
import bson
import logging
import os

import pymongo

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


def get_all_posts(criteria=None):
    logger.debug('Preparing to get all posts')
    col = _get_posts_col()
    if not criteria:
        return col.find()
    return col.find(criteria)


def delete_post(post_id):
    """Delete post by id""" 
    col = _get_posts_col()
    col.delete_one({"_id": bson.ObjectId(post_id)})
