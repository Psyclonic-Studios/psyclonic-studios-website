from trello import TrelloClient, Label
from server.secrets import TRELLO_API_KEY, TRELLO_SECRET_API_KEY

client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_SECRET_API_KEY
)

PSYCLONIC_BOARD_ID = 'DqmfTdPc'
CUSTOMER_LIST_ID = '5de811ce9749334e9e07ca08'
BUYER_LABEL = Label(client,'5de82868f328f04d1b696bae', '')
ENQUIRY_LABEL = Label(client,'5de9e194d0b96b70951ad035', '')

def create_customer_card(title, **kwargs):
    client.get_list(CUSTOMER_LIST_ID).add_card(title, **kwargs)