from trello import TrelloClient, Label
import os
import pickle

creds = None
if os.path.exists('trello_token.pickle'):
    with open('trello_token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    raise ValueError('Cannot find trello credentials')

client = TrelloClient(
    api_key=creds['public'],
    api_secret=creds['secret']
)

PSYCLONIC_CUSTOMER_BOARD_ID = 'KQYuol12'

AWAITING_RESPONSE_LIST_ID = '5df9b707d14de457c9c131d7'
PAYMENT_RECIEVED_LIST_ID = '5df9b7375786244287e0bc92'

ONLINE_ORDER_LABEL = Label(client, '5df9b6c2af988c41f25aba6e', '')
ARTWORK_ENQUIRY_LABEL = Label(client, '5df9b6c2af988c41f25aba6f', '')
SHIPPING_ENQUIRY_LABEL = Label(client, '5df9b6c2af988c41f25aba70', '')

def create_customer_card(list_id, title, **kwargs):
    client.get_list(list_id).add_card(title, **kwargs)