"""
File: manage_exchange_url_info.py
Description: this file provides a class 'Exchange_Info_Manager' for managing and loading the api info from redis.
Author: Jerry
Date  : 2025-01-21
Version: 1.0.0
Update Record:
-- 2025-01-21: initialize version 1.0.0;
"""
import redis
import json
from typing import List, Dict,Any
from global_manager import Global_Variable_Manager
from fake_useragent import UserAgent
global_variable_manager = Global_Variable_Manager()
import requests

class Exchange_Url_Info_Manager:
    def __init__(self,redis_client: redis.StrictRedis=None):
        if redis_client:
            self.redis_client = redis_client
        else:
            redis_client = global_variable_manager.get(variable_name="redis_client")
            if not redis_client:
                redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
                global_variable_manager.add(variable_name="redis_client", variable_value=redis_client)
            self.redis_client = redis_client

        self.__kline_parameter = {"interval":"1d",
                                "startTime":None,
                                "endTime":None,
                                "limit":365}
        ua = UserAgent()
        random_user_agent = ua.random
        self.header = {"User-Agent": random_user_agent}


    def load_request_info(self,exchange:str, request_data_type:List[str],symbol:List[str],
                          asset_type:str,is_microsecond: bool=True,
                          api_type: str="websocket_api",**kwargs) -> Dict:
        try:
            if api_type == "websocket_api":
                '''
                # By the principle of First Argument First Checking, this part should be taken on the calling party.
                if isinstance(symbol, str):
                    symbol = [symbol]
                symbol = [_.lower() for _ in symbol]

                if isinstance(request_data_type, str):
                    request_data_type = [request_data_type]
                '''

                request_info = self.__load_websocket_request_info(exchange=exchange,
                                                                  request_data_type=request_data_type,
                                                                  symbol=symbol,
                                                                  asset_type=asset_type,
                                                                  is_microsecond=is_microsecond)
                return request_info

            elif api_type == "rest_api":
                request_info = self.__load_rest_request_info(exchange=exchange,
                                                             request_data_type=request_data_type,
                                                             symbol=symbol,
                                                             asset_type=asset_type,
                                                             is_microsecond=is_microsecond,
                                                             **kwargs
                                                             )
                return request_info
            else:
                raise ValueError(f"api_type only supports: 'websocket_api' and 'rest_api'.")

        except Exception as e:
            print(e)




    def __load_websocket_request_info(self,exchange:str,request_data_type:List[str],
                                      symbol:List[str],asset_type:str,
                                      is_microsecond: bool=True) -> Dict:

        try:
            request_info = {}
            request_info[f"websocket_base_url"] = self.redis_client.hget(exchange+"_Api",
                                                                         f"{asset_type}BaseWebsocketApi")
            capitalize_first_letter = lambda word: word[0].upper() + word[1:]
            request_data_type = [f"{asset_type}{capitalize_first_letter(word)}" for word in request_data_type]
            if is_microsecond:
                '''
                Note binance websocket/rest supports returning data in microseconds, which may implies the unfitted problems in
                other exchanges. (2025/01/21, Jerry)
                '''
                request_info[f"websocket_base_url"] = request_info[f"websocket_base_url"] + "?timeUnit=microsecond"

            params = [f"{_symbol}{self.redis_client.hget(exchange+"_Api", _request_data_type+ "WebsocketApi")}" for _symbol in symbol
                      for _request_data_type in request_data_type]
            # print(f"params: {params}")
            message = {"method": "SUBSCRIBE", "params": params, "id": 1}
            request_message = json.dumps(message)
            request_info["subscribe_message"] = request_message

            # print(request_info)

            return request_info
        except Exception as e:
            print(e)

    def __load_rest_request_info(self,exchange:str,
                                 request_data_type:List[str],symbol:List[str],
                                 asset_type:str,is_microsecond: bool=True,**kwargs) -> Dict:
        try:
            request_info = {}
            request_info["restapi_base_url"] = self.redis_client.hget(exchange + "_Api",
                                                                      f"{asset_type}BaseRestApi")
            capitalize_first_letter = lambda word: word[0].upper() + word[1:]
            end_point_key = f"{asset_type}{capitalize_first_letter(request_data_type[0])}RestApi"
            end_point = self.redis_client.hget(exchange + "_Api", end_point_key)


            if "parameter" in kwargs:
                if kwargs["parameter"] == None and request_data_type[0] == "kline":
                    parameter = self.__kline_parameter  # only for kline parameter, controlled by instancialization;
                    if len(symbol) == 1:
                        parameter["symbol"] = symbol[0]
                        parameter = {k: v for k, v in parameter.items() if v is not None}
                    else:
                        # async tasks with multiple symbols
                        async_task_parameter = {}
                        for _symbol in symbol:
                            _parameter = parameter
                            _parameter["symbol"] = _symbol
                            _parameter = {k: v for k, v in _parameter.items() if v is not None}
                            async_task_parameter[_symbol] = _parameter
                        parameter = async_task_parameter
                else:
                    parameter = kwargs["parameter"]
            else:
                parameter = kwargs["parameter"]


            request_info["parameter"] = parameter

            #request_info["parameter"] =



            if "header" in kwargs:
                if kwargs["header"]:
                    request_info["header"] = kwargs["header"]
                else:
                    request_info["header"] = self.header
            else:
                request_info["header"] = self.header
            # print(f"test: {request_info}")

            if is_microsecond:
                '''
                Note binance websocket/rest supports returning data in microseconds, which may implies the unfitted problems in
                other exchanges. (2025/01/21, Jerry)
                '''
                request_info["header"]["X-MBX-TIME-UNIT"] = "microsecond"


            if end_point:
                request_info["restapi_url"] = request_info["restapi_base_url"] + end_point
            else:
                request_info["restapi_url"] = request_info["restapi_base_url"]

            # test
            '''
            response = requests.get(url=request_info["restapi_url"],params=parameter,headers=request_info["header"])
            data = response.json()
            print(data)

            '''


            return request_info
        except Exception as e:
            print(e)

    def update_request_info(self,exchange:str,key:str,value:str) -> Any:
        try:
            self.redis_client.hset(exchange, key, value)
            return self.redis_client.hget(exchange,key)
        except Exception as e:
            print(e)


def test_load_request_info():
    redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    info_manager = Exchange_Url_Info_Manager(redis_client=redis_client)
    result = info_manager.load_request_info(exchange="Binance",
                                            symbol=["BTCUSDT"],
                                            request_data_type=["tickTrade"],
                                            asset_type="spot",
                                            api_type="websocket_api",
                                            is_microsecond=True,
                                            )

    print(result)










if __name__ == '__main__':
    test_load_request_info()
