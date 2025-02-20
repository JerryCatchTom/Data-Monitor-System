'''
@File: binance_url_info_manager.py
@Description: ... ;
@Author: Jerry ;
@Date  : 27/1/25
Version: 1.0.0
Update Record:
-- 27/1/25: initialize version 1.0.0;
'''

from typing import List
import tomli
import json
from typing import Any
from fake_useragent import UserAgent


from Configuration_File_Manage.Exchange_Url_Info_Manager.base_url_info_manager import (Base_Url_Info_Manager,
                                                                                       Base_Rest_Api_Manager,
                                                                                       Base_Websocket_Api_Manager)
from global_manager import Global_Variable_Manager, PROJECT_ROOT
global_variable_manager = Global_Variable_Manager()

class Binance_Url_Info_Manager(Base_Url_Info_Manager):

    def __init__(self):
        self.exchange = "binance"
        self.__support_api_type = ["rest_api","websocket_api"]
        self.__support_asset_type = ["spot"]
        self.__config_file_path = (PROJECT_ROOT / "Configuration_File_Manage" / "Exchange_Url_Info_Config" /
                                   "binance_url_info.toml")
        self.config_info = self.__load_config_info()
        self.__rest_api_manager = Rest_Api_Manager(config_info=self.config_info)
        self.__websocket_api_manager = Websocket_Api_Manager(config_info=self.config_info)
        self.__api_manager = {"rest_api": self.__rest_api_manager,
                              "websocket_api": self.__websocket_api_manager}







    def load_request_info(self,request_data_type:List[str],symbol:List[str],
                          api_type: str, asset_type:str=None,
                          is_microsecond: bool=True,**kwargs) -> dict:

        if api_type not in self.__support_api_type:
            raise KeyError(f"{self.exchange} only supports "
                             f"{self.__support_api_type}, but receive '{api_type}'.")

        if asset_type:
            if asset_type not in self.__support_asset_type:
                raise KeyError(f"{self.exchange} only supports "
                                 f"{self.__support_asset_type}, but receive '{asset_type}'.")


        api_manager = self.__api_manager[api_type]
        request_info = api_manager.load_request_info(request_data_type=request_data_type,
                                                     symbol=symbol,
                                                     asset_type=asset_type,
                                                     is_microsecond=is_microsecond,
                                                     **kwargs)

        return request_info


    def __load_config_info(self):
        config_info = global_variable_manager.get("binance_url_info")
        if config_info:
            return config_info
        else:
            with open(self.__config_file_path, "rb") as f:
                config_info = tomli.load(f)

            global_variable_manager.add(variable_name="binance_url_info",
                                        variable_value=config_info)
            return config_info


class Websocket_Api_Manager(Base_Websocket_Api_Manager):
    def __init__(self,config_info:Any):
        self.config_info = config_info

    def load_request_info(self,
                          request_data_type:str,
                          symbol:List[str],
                          asset_type:str,
                          is_microsecond: bool,
                          **kwargs):
        request_info = {}
        websocket_base_api = self.config_info[asset_type]["websocket_base_api"]
        request_info[f"websocket_base_url"] = websocket_base_api
        if is_microsecond:
            '''
            Note binance websocket/rest supports returning data in microseconds, which may implies the unfitted problems in
            other exchanges. (2025/01/21, Jerry)
            '''
            request_info[f"websocket_base_url"] = request_info[f"websocket_base_url"] + "?timeUnit=microsecond"

        parameter = [f"{_symbol}{self.config_info[asset_type]["websocket_api"][request_data_type]}"
                     for _symbol in symbol]

        message = {"method": "SUBSCRIBE", "params": parameter, "id": 1}
        request_message = json.dumps(message)
        request_info["subscribe_message"] = request_message

        # print(request_info)

        return request_info


class Rest_Api_Manager(Base_Rest_Api_Manager):
    def __init__(self, config_info: Any):
        self.config_info = config_info
        self.__support_request_data_type = {"kline" : self.__load_kline_request_info,
                                            "asset_info":self.__load_asset_request_info}

    def load_request_info(self, request_data_type:str,symbol:List[str],
                          asset_type:str=None,
                          is_microsecond: bool=True,**kwargs):

        try:
            request_info = {}

            # rest_api does not support multiple request data type like ["kline", "asset_info]

            rest_base_api = self.config_info[asset_type]["rest_base_api"]
            request_info[f"rest_base_url"] = rest_base_api

            end_point = self.config_info[asset_type]["rest_api"][request_data_type]
            request_info[f"rest_base_url"] = request_info[f"rest_base_url"] + end_point





            request_info = self.__support_request_data_type[request_data_type](request_info=request_info,
                                                                               request_data_type=request_data_type,
                                                                               symbol=symbol,
                                                                               asset_type=asset_type,
                                                                               is_microsecond=is_microsecond,
                                                                               **kwargs)
            # print(request_info)

            return request_info
        except Exception as e:
            print(e)
            return None

    def __load_random_header(self):
        ua = UserAgent()
        random_user_agent = ua.random
        return {"User-Agent": random_user_agent}
    def __load_kline_request_info(self,request_info:dict,symbol:List[str],is_microsecond: bool,**kwargs):

        # load parameter
        if "parameter" in kwargs:
            parameter = kwargs["parameter"]
        else:
            parameter = {"interval": "1d",
                         "startTime": None,
                         "endTime": None,
                         "limit": 365}

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
        request_info["parameter"] = parameter

        # load header
        if "header" in kwargs:
            if kwargs["header"]:
                request_info["header"] = kwargs["header"]
            else:
                request_info["header"] = self.__load_random_header()
        else:
            request_info["header"] = self.__load_random_header()
        # print(f"test: {request_info}")

        if is_microsecond:
            '''
            Note binance websocket/rest supports returning data in microseconds, which may implies the unfitted problems in
            other exchanges. (2025/01/21, Jerry)
            '''
            request_info["header"]["X-MBX-TIME-UNIT"] = "microsecond"

        return request_info

    def __load_asset_request_info(self,request_info:dict,**kwargs):

        if "header" in kwargs:
            if kwargs["header"]:
                request_info["header"] = kwargs["header"]
            else:
                request_info["header"] = self.__load_random_header()
        else:
            request_info["header"] = self.__load_random_header()

        return request_info




def test_url_manager():
    test_manager = Binance_Url_Info_Manager()
    result = test_manager.load_request_info(symbol=["BTCUSDT"],
                                   request_data_type=["asset_info"],
                                   asset_type="spot",
                                   api_type="rest_api",
                                   is_microsecond=True,

                                  )
    print(result)

if __name__ == '__main__':
    test_url_manager()