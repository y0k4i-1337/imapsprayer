import urllib3
from .common.socksimap import SocksIMAP4, SocksIMAP4SSL
from imaplib import IMAP4, IMAP4_SSL, IMAP4_PORT, IMAP4_SSL_PORT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)