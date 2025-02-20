'''
@File: parse_exchange_market_data.py
@Description: this is the key component of Parse_Data Module to provide parsing all trading data
                (like MarketDepth, TickTrade)
@Author: Jerry ;
@Date  : 23/1/25
Version: 1.0.0
Update Record:
-- 23/1/25: initialize version 1.0.0;
'''
import time
import json
import orjson
import capnp
import tempfile
from typing import Tuple,TypeAlias,Any,List
from capnp.lib.capnp import _StructModule,_DynamicStructReader

from Configuration_File_Manage.manage_exchange_market_data_parse_struct import Market_Data_Parse_Info_Manager

from global_manager import Global_Variable_Manager
global_variable_manager = Global_Variable_Manager()
CapnpStruct: TypeAlias = _StructModule
DeserializedCapnpStruct: TypeAlias = _DynamicStructReader


class Market_Data_Parser:
    def __init__(self):
        self.__support_exchange = {"binance":None}
        self.market_data_parse_info_manager = Market_Data_Parse_Info_Manager()


    def parse_data(self,exchange:str, asset_type:str, parse_struct_type:str,data:Any,
                   is_batch:bool=False):

        try:
            mapping_struct, parse_struct = self.__load_parse_info(exchange=exchange,
                                                                  asset_type=asset_type,
                                                                  parse_struct_type=parse_struct_type)


            if is_batch:
                parsed_message = self.__parse_batch_data(mapping_struct=mapping_struct,
                                                         parse_struct=parse_struct,
                                                         data=data)
            else:
                # need to check this part: Jerry,20250210
                symbol, parsed_message = self.__parse_single_data(mapping_struct=mapping_struct,
                                                                  parse_struct=parse_struct,
                                                                  data=data,)


            return symbol, parsed_message


        except Exception as e:
            print(e)
            return None,None


    def deserialize_capnp(self,exchange:str, asset_type:str, parse_struct_type:str,data:Any,):
        mapping_struct, parse_struct = self.__load_parse_info(exchange=exchange,
                                                              asset_type=asset_type,
                                                              parse_struct_type=parse_struct_type,
                                                              )
        with parse_struct.from_bytes(data) as deserialized_message:
            return deserialized_message ##


    def __parse_single_data(self,mapping_struct:dict,parse_struct:CapnpStruct,data:Any,):
        data = orjson.loads(data)

        if "symbol" in mapping_struct:
            symbol = data[mapping_struct["symbol"]]
        else:
            # "Some structs may not provide the symbol info."
            symbol = None

        mapping_message = None
        try:
            mapping_message = {capnp_key: data[data_key] for capnp_key,data_key,
                                                         in mapping_struct.items()}
        except Exception as e:
            print(e)
            return None,mapping_message

        parsed_message = parse_struct.new_message(**mapping_message).to_bytes()
        return symbol, parsed_message

    def __parse_batch_data(self,mapping_struct:dict,parse_struct:CapnpStruct,data:List):
        # need to check this function
        batch_data = orjson.loads(f"[{','.join(data)}]")

        parsed_batch_message = [
            parse_struct.new_message(**{capnp_key: _data[data_key] for capnp_key,data_key
                                                     in mapping_struct.items()}).to_bytes()
            for _data in batch_data
        ]
        return parsed_batch_message


    def __load_parse_info(self,exchange:str, asset_type:str, parse_struct_type:str,):
        try:
            mapping_struct = self.market_data_parse_info_manager.load_mapping_struct(exchange=exchange,
                                                                                     asset_type=asset_type,
                                                                                     request_data_type=parse_struct_type)

            parse_struct = self.market_data_parse_info_manager.load_parse_struct(exchange=exchange,
                                                                                 asset_type=asset_type,
                                                                                 request_data_type=parse_struct_type)

            return mapping_struct,parse_struct

        except Exception as e:
            print(e)
            return None

    def convert_snake_to_camel(self,name: str) -> str:

        return ''.join(word.capitalize() for word in name.split('_'))



def agg_trade_sample():
    test_json_data = {
        "e": "aggTrade",
        "E": 1672515782136,
        "s": "BNBBTC",
        "a": 12345,
        "p": "0.001",
        "q": "100",
        "f": 100,
        "l": 105,
        "T": 1672515782136,
        "m": True,
        "M": True
    }

    json_sample = orjson.dumps(test_json_data)
    return json_sample
def test_():
    test_json_data = {
        "e": "aggTrade",
        "E": 1672515782136,
        "s": "BNBBTC",
        "a": 12345,
        "p": "0.001",
        "q": "100",
        "f": 100,
        "l": 105,
        "T": 1672515782136,
        "m": True,
        "M": True
    }
    json_sample = agg_trade_sample()
    orjson.loads(json_sample)
    parser = Market_Data_Parser()
    parsed_data = parser.parse_data(exchange="binance",
                      asset_type="spot",
                      parse_struct_type="aggregate_trade",
                      data=json_sample)
    test = parser.deserialize_capnp(exchange="binance",
                      asset_type="spot",
                      parse_struct_type="aggregate_trade",
                             data=parsed_data)
    print("test ...")
    print(test)


if __name__ == '__main__':
    #test_data_parse_manager()
    test_()


