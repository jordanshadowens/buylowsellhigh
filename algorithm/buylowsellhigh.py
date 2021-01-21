import asyncio
import pickle
from market.market import Market
from util.generator import Generator

asklist = []
openasklist = open("asklist.pickle", "wb")
pickle.dump(asklist, openasklist)
openasklist.close()

class Buylow:

    def __init__(self, session, account, base_url):
        self.session = session
        self.account = account
        self.base_url = base_url

    def start_script(self):
        loop = asyncio.get_event_loop()

        def calculatetodaysmovingaverage():
            readasklist = open("asklist.pickle", "rb")
            asklist = pickle.load(readasklist)
            readasklist.close()

            market = Market(self.session, self.base_url, self.account)
            ask = market.quotes()

            asklist.append(ask)
            openasklist = open("asklist.pickle", "wb")
            pickle.dump(asklist, openasklist)
            openasklist.close()

            print("Ask Price: ")
            print(ask)

            loop.call_later(300, calculatetodaysmovingaverage)

        def createbuyorder():
            readasklist = open("asklist.pickle", "rb")
            asklist = pickle.load(readasklist)
            readasklist.close()

            total = 0
            count = 0

            for ask in asklist:
                total = ask + total
                count = count + 1

            movingaverageFunc = lambda a, b: a / b
            movingaverage = movingaverageFunc(total, count)

            print("Today's Moving Average: ")
            print(movingaverage)
            market = Market(self.session, self.base_url, self.account)
            ask = market.quotes()
            if ask < movingaverage:
                def buy():
                    clientorderId = Generator.get_random_alphanumeric_string(20)

                    # Add payload for POST Request
                    payload = """<PreviewOrderRequest>
                                                      <orderType>EQ</orderType>
                                                      <clientOrderId>{0}</clientOrderId>
                                                      <Order>
                                                          <allOrNone>false</allOrNone>
                                                          <priceType>LIMIT</priceType>
                                                          <orderTerm>GOOD_FOR_DAY</orderTerm>
                                                          <marketSession>REGULAR</marketSession>
                                                          <stopPrice></stopPrice>
                                                          <limitPrice>{1}</limitPrice>
                                                          <Instrument>
                                                              <Product>
                                                                  <securityType>EQ</securityType>
                                                                  <symbol></symbol>
                                                              </Product>
                                                              <orderAction>{2}</orderAction>
                                                              <quantityType>QUANTITY</quantityType>
                                                              <quantity>1</quantity>
                                                          </Instrument>
                                                      </Order>
                                                  </PreviewOrderRequest>"""
                    orderaction = "BUY"
                    payload = payload.format(clientorderId, ask, orderaction)
                    market.preview_order(payload, clientorderId, ask, orderaction)
                loop.call_soon(buy)
            loop.call_later(300, createbuyorder)


        def renew_token():
            url = self.base_url + "/oauth/renew_access_token"

            response = self.session.get(url, header_auth=True)
            print(response)
            loop.call_later(7100, renew_token)

        loop.call_soon(calculatetodaysmovingaverage)
        loop.call_later(7200, createbuyorder)
        loop.call_later(7100, renew_token)
        loop.run_forever()