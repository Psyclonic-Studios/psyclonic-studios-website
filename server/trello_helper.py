from trello import TrelloClient, Label
from server.secrets import TRELLO_API_KEY, TRELLO_SECRET_API_KEY

client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_SECRET_API_KEY
)

PSYCLONIC_CUSTOMER_BOARD_ID = 'KQYuol12'

AWAITING_RESPONSE_LIST_ID = '5df9b707d14de457c9c131d7'
PAYMENT_RECIEVED_LIST_ID = '5df9b7375786244287e0bc92'

ONLINE_ORDER_LABEL = Label(client, '5df9b6c2af988c41f25aba6e', '')
ARTWORK_ENQUIRY_LABEL = Label(client, '5df9b6c2af988c41f25aba6f', '')
SHIPPING_ENQUIRY_LABEL = Label(client, '5df9b6c2af988c41f25aba70', '')

def create_customer_card(title, **kwargs):
    client.get_list(PAYMENT_RECIEVED_LIST_ID).add_card(title, **kwargs)