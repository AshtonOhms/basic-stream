import random
import redis
import string

SESSION_ID_LENGTH = 6

session_store = redis.Redis(host='redis', port=6379)

def set_user_status(session_id, user_id, watch_time):
    pass

def create_session(video_id):
    session_id = _generate_session_id()
    video_key = _get_video_key(session_id)

    session_store.set(video_key, video_id.encode("utf-8"))

    return session_id

def get_session_video_id(session_id):
    video_key = _get_video_key(session_id)

    return session_store.get(video_key).decode("utf-8")

def join_session(user_id, session_id):
    users_key = _get_users_key(session_id)

    session_store.sadd(users_key, user_id)
    
def _generate_session_id():
    chars = ''.join(set(string.hexdigits.lower()))
    return ''.join(random.choice(chars) for i in range(SESSION_ID_LENGTH))

def _get_video_key(session_id):
    return "session-%s-video" % session_id

def _get_users_key(session_id):
    return "session-%s-users" % session_id

def _get_user_status_key(session_id, user_id):
    return "session-%s-user-%s" % session_id
