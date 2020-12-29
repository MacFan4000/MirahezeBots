"""The functions in this file are not suitable for non-internal use. They are subject to change without notice and are not yet released."""
import requests


def login(url, session, username='Example', password='password'):
    """Login to MediaWiki API using bot password system."""
    CONNECTERRMSG = "Unable to conect to wiki"
    PARAMS_0 = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json',
    }
    try:
        request = session.get(url=url, params=PARAMS_0)
        DATA = request.json()
    except Exception:
        return ["Error", CONNECTERRMSG]

    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

    PARAMS_1 = {
        'action': 'login',
        'lgname': username,
        'lgpassword': password,
        'lgtoken': LOGIN_TOKEN,
        'format': 'json',
    }
    try:
        session.post(url, data=PARAMS_1)
    except Exception:
        return ["Error", CONNECTERRMSG]
    return ["Success", "Logged in"]


def gettoken(url, session, type='csrftoken'):
    """Get a token from the meta::tokens api."""
    PARAMS_2 = {'action': 'query', 'meta': 'tokens', 'format': 'json'}

    try:
        request = session.get(url=url, params=PARAMS_2)
        DATA = request.json()
    except Exception:
        return ["Error", "Unable to conect to wiki"]

    TOKEN = DATA['query']['tokens'][type]
    return TOKEN


def makeaction(requestinfo, action, target, performer, reason, content=''):
    """Perform an action via the ACTIONS API."""
    if action == 'edit':
        PARAMS = {
            'action': 'edit',
            'title': target,
            'summary': reason + ' (' + performer + ')',
            'appendtext': '\n* ' + performer + ': ' + reason,
            'token': requestinfo[2],
            'bot': 'true',
            'format': 'json',
        }
    elif action == "create":
        PARAMS = {
            'action': 'edit',
            'title': target,
            'summary': reason,
            'text': content,
            'token': requestinfo[2],
            'bot': 'true',
            'format': 'json',
            'contentmodel': 'wikitext',
            'recreate': True,
            'watchlist': 'nochange',
        }

    elif action == 'block':
        PARAMS = {
            'action': 'block',
            'user': target,
            'expiry': 'infinite',
            'reason': 'Blocked by ' + performer + ' for ' + reason,
            'bot': 'false',
            'token': requestinfo[2],
            'format': 'json',
        }

    elif action == 'unblock':
        PARAMS = {
            'action': 'unblock',
            'user': target,
            'reason': 'Requested by ' + performer + ' Reason: ' + reason,
            'token': requestinfo[2],
            'format': 'json',
        }

    elif action == 'delete':
        PARAMS = {
            'action': 'delete',
            'title': target,
            'reason': 'Requested by ' + performer + ' Reason: ' + reason,
            'token': requestinfo[2],
            'format': 'json',
        }

    try:
        request = requestinfo[1].post(requestinfo[0], data=PARAMS)
        DATA = request.json()
        if DATA.get("error") is not None:
            return ["MWError", (DATA.get("error").get("info"))]
        else:
            return ["Success", ("{0} request sent. You may want to check the {0} log to be sure that it worked.").format(action)]
    except Exception:
        return ["Fatal", ("An unexpected error occurred. Did you type the wiki or user incorrectly? Do I have {} rights on that wiki?").format(action)]


def main(performer, target, action, reason, url, authinfo, content=False):
    """Execute a full API Sequence."""
    session = requests.Session()
    lg = login(url, session, authinfo[0], authinfo[1])
    if lg[0] == "Error":
        return lg[1]
    else:
        TOKEN = gettoken(url, session, type='csrftoken')
        if TOKEN[0] == "Error":
            return TOKEN[1]
        else:
            if content:
                act = makeaction([url, session, TOKEN], action, target, performer, reason, content)
            else:
                act = makeaction([url, session, TOKEN], action, target, performer, reason)
            return act[1]
