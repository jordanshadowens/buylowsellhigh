import json
import logging
import configparser
from logging.handlers import RotatingFileHandler
from algorithm.buylowsellhigh import Buylow

# loading configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# logger settings
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)

class Accounts:

    def __init__(self, session, base_url):
        """
        Initialize Accounts object with session and account information

        :param session: authenticated session
        """
        self.session = session
        self.account = {}
        self.base_url = base_url

    def account_list(self):
        """
        Calls account list API to retrieve a list of the user's E*TRADE accounts

        :param self:Passes in parameter authenticated session
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/list.json"

        # Make API call for GET request
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

            data = response.json()
            if data is not None and "AccountListResponse" in data and "Accounts" in data["AccountListResponse"] \
                    and "Account" in data["AccountListResponse"]["Accounts"]:
                accounts = data["AccountListResponse"]["Accounts"]["Account"]
                while True:
                    # Display account list
                    count = 1
                    print("\nBrokerage Account List:")
                    accounts[:] = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                    for account in accounts:
                        print_str = str(count) + ")\t"
                        if account is not None and "accountId" in account:
                            print_str = print_str + (account["accountId"])
                        if account is not None and "accountDesc" in account \
                                and account["accountDesc"].strip() is not None:
                            print_str = print_str + ", " + account["accountDesc"].strip()
                        if account is not None and "institutionType" in account:
                            print_str = print_str + ", " + account["institutionType"]
                        print(print_str)
                        count = count + 1
                    print(str(count) + ")\t" "Go Back")

                    # Select account option
                    account_index = input("Please select an account: ")
                    if account_index.isdigit() and 0 < int(account_index) < count:
                        if self.base_url == "":
                            self.account = accounts[int(account_index) - 1]
                        else:
                            self.account = accounts[int(account_index) - 1]

                        buylow = Buylow(self.session, self.account, self.base_url)
                        buylow.start_script()

                    elif account_index == str(count):
                        break
                    else:
                        print("Unknown Account Selected!")
            else:
                # Handle errors
                logger.debug("Response Body: %s", response.text)
                if response is not None and response.headers['Content-Type'] == 'application/json' \
                        and "Error" in response.json() and "message" in response.json()["Error"] \
                        and response.json()["Error"]["message"] is not None:
                    print("Error: " + data["Error"]["message"])
                else:
                    print("Error: AccountList API service error")
        else:
            # Handle errors
            logger.debug("Response Body: %s", response.text)
            if response is not None and response.headers['Content-Type'] == 'application/json' \
                    and "Error" in response.json() and "message" in response.json()["Error"] \
                    and response.json()["Error"]["message"] is not None:
                print("Error: " + response.json()["Error"]["message"])
            else:
                print("Error: AccountList API service error")
