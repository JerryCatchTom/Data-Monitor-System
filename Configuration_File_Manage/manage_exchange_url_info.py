'''
@File: manage_exchange_url_info.py
Description: this file provides a class 'Exchange_Info_Manager' for managing and loading the api info from redis.
Author: Jerry
Date  : 2025-01-21
Version: 1.1.0
Update Record:
-- 2025-01-21: initialize version 1.0.0;
-- 2025-01-27: update version 1.1.0: reframe the manage structure;
'''

from typing import List, Dict, Any
from global_manager import Global_Variable_Manager
from Configuration_File_Manage.Exchange_Url_Info_Manager.binance_url_info_manager import Binance_Url_Info_Manager

global_variable_manager = Global_Variable_Manager()

class Exchange_Url_Info_Manager:
    def __init__(self):
        self.__support_exchange = {"binance":Binance_Url_Info_Manager()}

    def load_request_info(self,exchange:str,api_type:str,request_data_type:str,asset_type:str,**kwargs):

        if exchange in self.__support_exchange:
            exchange_url_info_manager = self.__support_exchange[exchange]
            request_info = exchange_url_info_manager.load_request_info(exchange=exchange,
                                                                       api_type=api_type,
                                                                       request_data_type=request_data_type,
                                                                       asset_type=asset_type,
                                                                       **kwargs)
            # print(request_info)
            return request_info

        else:
            raise KeyError(f"exchange only supports {self.__support_exchange.keys()},but receive {exchange}.")







def test_load_request_info():

    info_manager = Exchange_Url_Info_Manager()
    result = info_manager.load_request_info(exchange="binance",
                                            symbol=["BTCUSDT","ETHUSDT"],
                                            request_data_type="kline",
                                            asset_type="spot",
                                            api_type="rest_api",
                                            is_microsecond=True,

                                            )
    print("test")
    print(result)










if __name__ == '__main__':
    test_load_request_info()