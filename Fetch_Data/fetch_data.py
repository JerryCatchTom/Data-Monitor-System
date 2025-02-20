import asyncio
import time
import redis
import websockets
import uvloop
import json
import ssl
import certifi
import requests
import aiohttp
from Configuration_File_Manage.manage_exchange_url_info import Exchange_Url_Info_Manager
from Parse_Data.parse_exchange_market_data import Market_Data_Parser

# from Data_Store.clickhouse_manager import exchange_info_insert,database_executor,insert_dataframe_to_table
from fake_useragent import UserAgent
import pandas as pd
from Alert_Monitor import exception_marker
import logging

from typing import List,Dict,Tuple



asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Websocket_API_Data_Fetcher:

    def __init__(self):
        self.exchange_url_info_manager = Exchange_Url_Info_Manager()
        self.market_data_parser = Market_Data_Parser()
        self.queue = asyncio.Queue()
        self.task_manager: Dict[Tuple[str, str, str], asyncio.Task] = {} # (exchange, asset_type, symbol)

    async def async_fetch_task(self, exchange:str, request_data_type:str,
                               symbol:List[str], asset_type:str, is_microsecond:bool):


        request_info = self.exchange_url_info_manager.load_request_info(exchange=exchange,
                                                                        request_data_type=request_data_type,
                                                                        symbol=symbol,
                                                                        asset_type=asset_type,
                                                                        is_microsecond=is_microsecond,
                                                                        api_type="websocket_api")



        ssl_context = ssl.create_default_context(cafile=certifi.where())
        count = 0

        async with websockets.connect(request_info["websocket_base_url"], ssl=ssl_context) as websocket:
            await websocket.send(request_info['subscribe_message'])
            # print(f"WebSocket Data Monitoring: {exchange}-{asset_type}-{symbol}")
            async for message in websocket:
                '''
                print(message)
                json_data = json.loads(message)
                print(json_data)
                print(f"count = {count}")
                count += 1
                '''

                await self.queue.put((exchange, asset_type, symbol, message))

    async def fetch_data(self,exchange:str,request_data_type:str,
                   symbol:List[str], asset_type:str,is_microsecond:bool=True):

        symbol = [_symbol.lower() for _symbol in symbol]


        task = asyncio.create_task(self.async_fetch_task(exchange=exchange,
                                                         request_data_type=request_data_type,
                                                         symbol=symbol,
                                                         asset_type=asset_type,
                                                         is_microsecond=is_microsecond))


        while True:
            yield await self.queue.get()
    async def load_data(self):
        pass

    def stop_task(self, exchange: str, asset_type: str, symbol: str):
        asyncio.run(self.async_stop_task(exchange, asset_type, symbol))

    async def async_stop_task(self, exchange: str, asset_type: str, symbol: str):
        task_key = (exchange, asset_type, symbol)
        if task_key in self.task_manager:
            self.task_manager[task_key].cancel()
            try:
                await self.task_manager[task_key]
            except asyncio.CancelledError:
                print(f"WebSocket Task: {exchange}-{asset_type}-{symbol} Successful cancelled.")
            del self.task_manager[task_key]
        else:
            print(f"No Found WebSocket Task: {exchange}-{asset_type}-{symbol}")

    def stop_all_tasks(self):

        asyncio.run(self.async_stop_all_tasks())

    async def async_stop_all_tasks(self):
        """
        停止所有 WebSocket 任务（异步方法）
        """
        for task_key in list(self.task_manager.keys()):
            self.task_manager[task_key].cancel()
            try:
                await self.task_manager[task_key]
            except asyncio.CancelledError:
                print(f"🛑 任务已取消: {task_key}")
            del self.task_manager[task_key]

class Rest_API_Data_Fetcher:

    def __init__(self):
        self.exchange_url_info_manager = Exchange_Url_Info_Manager()

        self.__support_rest_api_request_data_type = ["kline", "exchangeInfo"]

    def sync_fetch_data(self, exchange:str, request_data_type:List[str],
                        symbol:List[str]=[], asset_type:str=None,
                        header:dict=None,parameter:dict=None,is_microsecond:bool=True,**kwargs):



        try:
            if request_data_type[0] not in self.__support_rest_api_request_data_type:
                raise ValueError(f"request_data_type only supports {self.__support_rest_api_request_data_type} "
                                 f"but receives {request_data_type[0]} ")
            request_info = self.exchange_url_info_manager.load_request_info(exchange=exchange,
                                                                            request_data_type=request_data_type,
                                                                            symbol=symbol,
                                                                            asset_type=asset_type,
                                                                            is_microsecond=is_microsecond,
                                                                            api_type="rest_api",
                                                                            **kwargs)

            print('test')
            print(request_info)



            url = request_info["rest_base_url"]
            parameter = request_info["parameter"]
            header = request_info["header"]
            if parameter:
                json_data = requests.get(url=url, params=parameter, headers=header).json()
            else:
                json_data = requests.get(url=url, headers=header).json()
            print(json_data)
            return json_data

        except Exception as e:
            print(e)


    def async_fetch_data(self,exchange:str, request_data_type:List[str],
                        symbol:List[str]=[], asset_type:str=None,
                        header:dict=None,parameter:dict=None,is_microsecond:bool=True,
                        max_task_per_second=15,**kwargs):
        '''
        all async task from rest_api are based on different symbols with same url.
        '''
        if request_data_type[0] not in self.__support_rest_api_request_data_type:
            raise ValueError(
                {f"request_data_type only supports {self.__support_rest_api_request_data_type},"
                 f"but receives {request_data_type[0]}"})

        semaphore = asyncio.Semaphore(max_task_per_second)

        request_info = self.exchange_url_info_manager.load_request_info(exchange=exchange,
                                                                        request_data_type=request_data_type,
                                                                        symbol=symbol,
                                                                        asset_type=asset_type,
                                                                        is_microsecond=is_microsecond,
                                                                        api_type="rest_api",
                                                                        **kwargs)

        json_data = asyncio.run(self.__assemble_fetch_data_task(request_info=request_info,
                                                             semaphore=semaphore))

        # print(result)
        return json_data



    async def __async_fetch_data_task(self,symbol:str, request_info:dict,semaphore:asyncio.Semaphore) -> dict:
        async with semaphore:
            try:
                url = request_info["rest_base_url"]
                parameter = request_info["parameter"]
                header = request_info["header"]
                ssl_context = ssl.create_default_context(cafile=certifi.where())

                async with aiohttp.ClientSession() as session:
                        if parameter:
                            async with session.get(url, params=parameter, headers=header,ssl_context=ssl_context) as response:
                                json_data = await response.json()
                        else:
                            async with session.get(url, headers=header) as response:
                                json_data = await response.json()

                return {symbol: json_data}

            except Exception as e:
                print(e)
                return None


    async def __assemble_fetch_data_task(self,request_info:dict,semaphore:asyncio.Semaphore):
        async_parameter = request_info["parameter"]
        request_info["parameter"] = None

        task = []
        for _symbol,_parameter in async_parameter.items():
            _request_info = request_info
            _request_info["parameter"] = _parameter
            task.append(self.__async_fetch_data_task(symbol=_symbol,
                                                     request_info=_request_info,
                                                     semaphore=semaphore))

        response_result = await asyncio.gather(*task)
        json_data = {_symbol:_data for data in response_result for _symbol,_data in data.items() }
        return json_data





async def test_websocket_fetch():
    fetcher = Websocket_API_Data_Fetcher()

    exchange = "binance"
    asset_type = "spot"
    request_data_type = "tick_trade"
    symbol = ["btcusdt","ethusdt"]
    is_microsecond = True



    async for exchange, asset_type, symbol, msg in fetcher.fetch_data(exchange=exchange,
                                                                       request_data_type=request_data_type,
                                                                       symbol=symbol,
                                                                       asset_type=asset_type,
                                                                       is_microsecond=is_microsecond):
        print(f"Running: {exchange}-{asset_type}-{symbol} -> {msg}")

def test_fetch_data_by_rest_api():
    test_exchange = 'binance'
    test_request_data_type = ["kline"]
    test_symbol = ["BTCUSDT","ETHUSDT"]
    test_asset_type = "spot"

    test_gather = Rest_API_Data_Fetcher()
    test_gather.sync_fetch_data(exchange=test_exchange,
                                 request_data_type=test_request_data_type,
                                 symbol=test_symbol,
                                 asset_type=test_asset_type,
                                 is_microsecond=True
                                )


if __name__ == "__main__":


    asyncio.run(test_websocket_fetch())
    #test_fetch_data_by_rest_api()