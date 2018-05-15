#!/usr/bin/env python
# vim: set ts=4 sts=4 sw=4 et cindent ft=python:
"""
fetch basic message info for all messages in INBOX (From, subject, snippet
"""
from __future__ import print_function, unicode_literals, absolute_import

import oauth2client


from apiclient.discovery import build
from apiclient import errors

from httplib2 import Http

def get_gmail_service(cred_store='credentials.json', secrets='client_secrets.json', 
        scopes='https://www.googleapis.com/auth/gmail.readonly'):
    """
    Setup mail service using oauth2 credentials.
    May require browser confirmation
    """
    store = oauth2client.file.Storage(cred_store)
    creds = store.get()
    if not creds or creds.invalid:
        flow = oauth2client.client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = oauth2client.tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    return service



def get_message(service, message_id, user_id='me', **kwargs):
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Kwargs:
      whatever the api supports, but for example:
      q(str): gmail search box query ('from: x@y.com is:unread' etc)
      fields(str): comma-separated list of fields to return (makes it faster!)

    Returns:
      A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=message_id, **kwargs).execute()
        print ('Message snippet: {snippet}'.format(**message))
        return message

    except errors.HttpError as error:
        print ('An error occurred fetching message id {0}: {1}'.format(message_id, error))

def list_messages(service, user_id='me', **kwargs):
    """
    returns a list of messageids

    KWargs
      includeSpamTrash(bool)
      labelIds(list)
      maxResults(int)
      pageToken(str): 
    """
    counter = 0
    while True:
        try:
            response = service.users().messages().list(userId=user_id, **kwargs).execute()
            msglist = []
            if 'messages' in response:
                msglist.extend(response['messages'])
                counter += 1
            while 'nextPageToken' in response:
                print("Iteration: {}, Estimated Size: {resultSizeEstimate}, Next Page: {nextPageToken}".format(counter, **response))
                pt = response['nextPageToken']
                response = service.users().messages().list(userId=user_id, pageToken=pt, **kwargs).execute()
                msglist.extend(response['messages'])
                counter += 1
            return msglist

            # return [ m.get('id') for m in msglist['messages'] ]

        except errors.HttpError as error:
           print('An Error occured listing messages: {}'.format(error))

if __name__ == "__main__":

    svc = get_gmail_service()

    messageids = list_messages(svc, maxResults=500)
    print (len(messageids))


 
