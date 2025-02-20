'''
@File: central_data_manager.py
@Description: ... ;
@Author: Jerry ;
@Date  : 10/2/25
Version: 1.0.0
Update Record:
-- 10/2/25: initialize version 1.0.0;
'''
import zmq
import zmq.asyncio
import asyncio
import orjson
from typing import List,Any
from Fetch_Data.fetch_data import Websocket_API_Data_Fetcher
from Parse_Data.parse_exchange_market_data import Market_Data_Parser

'''
central data manager only works on websock api
'''

class Central_Data_Manager:
    def __init__(self, exchange:str, asset_type:str, request_data_type:str, symbol:List[str],is_microsecond:bool=True):
        self.exchange = exchange
        self.asset_type = asset_type
        self.request_data_type = request_data_type
        self.symbol = symbol
        self.is_microsecond = is_microsecond
        self.websocket_data_fetcher = Websocket_API_Data_Fetcher()
        self.parser = Market_Data_Parser()
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5555")

    def run(self):

        asyncio.run(self.__process_data())

    async def __process_data(self):
        async for exchange, asset_type, symbol, msg in self.websocket_data_fetcher.fetch_data(exchange=self.exchange,
                                                                                              request_data_type=self.request_data_type,
                                                                                              symbol=self.symbol,
                                                                                              asset_type=self.asset_type,
                                                                                              is_microsecond=self.is_microsecond):

            _symbol, parsed_message = self.parser.parse_data(exchange=self.exchange,
                                                            asset_type=self.asset_type,
                                                            parse_struct_type=self.request_data_type,
                                                            data=msg)


            # some unexpected receiving messages return None
            if not parsed_message:
                print(f"receive unknown msg {parsed_message},continue...")
                continue
            message_label = f"{exchange}-{asset_type}-{_symbol}-{self.request_data_type}"


            await self.__publish_data(message_label=message_label,message=parsed_message)

            print(f"Test Running: {message_label}")

    def __parse_data(self,message:Any):
        # test_data = self.test_sample()
        symbol, parsed_message = self.parser.parse_data(exchange=self.exchange,
                                                        asset_type=self.asset_type,
                                                        parse_struct_type=self.request_data_type,
                                                        data=message)


        '''
        test = self.parser.deserialize_capnp(exchange=self.exchange,
                                      asset_type=self.asset_type,
                                      parse_struct_type=self.request_data_type,
                                      data=parsed_message)
        print(parsed_message)
        print(test)
        print(symbol)
        '''
        return symbol,parsed_message



    async def __publish_data(self, message_label:str, message:Any):

        await self.socket.send_multipart([message_label.encode(),message])


    def test_sample(self):
        test_data = {"e":"trade","E":1739436780463744,"s":"BTCUSDT","t":4554048139,
                     "p":"95961.98000000","q":"0.07230000","T":1739436780462925,"m":False,"M":True}

        return orjson.dumps(test_data)



class Rest_Api_Data_Manager:
    def __init__(self):
        pass

def __test_central_manager():
    manager = Central_Data_Manager(exchange="binance",
                                   asset_type="spot",
                                   request_data_type="tick_trade",
                                   symbol=["BTCUSDT","ETHUSDT"])
    manager.run()

async def __test_publish():
    label = b"test_label"
    msg = b'\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x04\x00\x04\x00\xe7\xd7H\xb5b.\x06\x00\x1d\xf32\x10\x01\x00\x00\x00u\xd6H\xb5b.\x06\x00\x02\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x002\x00\x00\x00\r\x00\x00\x00B\x00\x00\x00\r\x00\x00\x00z\x00\x00\x00\x11\x00\x00\x00Z\x00\x00\x00trade\x00\x00\x00BTCUSDT\x0096212.11000000\x00\x000.00009000\x00\x00\x00\x00\x00\x00'
    context = zmq.asyncio.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://127.0.0.1:5555")
    print(f"sending: {label} -> {msg}")

    await pub_socket.send_multipart([label, msg])

    print(f"ZeroMQ publish done.")


if __name__ == '__main__':

    __test_central_manager()