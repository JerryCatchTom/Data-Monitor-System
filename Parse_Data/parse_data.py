'''
@File: parse_data.py
@Description: this is the key component of Parse_Data Module to provide parsing all trading data
                (like MarketDepth, TickTrade)
@Author: Jerry ;
@Date  : 23/1/25
Version: 1.0.0
Update Record:
-- 23/1/25: initialize version 1.0.0;
'''
import time
import redis
import json
import capnp
import tempfile
from global_manager import Global_Variable_Manager
from typing import Tuple,TypeAlias,Any
from capnp.lib.capnp import _StructModule,_DynamicStructReader

global_variable_manager = Global_Variable_Manager()
CapnpStruct: TypeAlias = _StructModule
DeserializedCapnpStruct: TypeAlias = _DynamicStructReader


class Data_Parse_Manager:
    def __init__(self,redis_client:redis.StrictRedis):
        self.redis_client = redis_client
        self.capnp_struct = {}
        self.mapping_struct = {}

    def parse_json_to_binary(self, exchange:str, json_data:dict,
                             parse_struct_key:str, mapping_struct_key:str)-> Tuple[int,bytes]:



        mapping_struct = self.__load_mapping_struct(exchange=exchange,
                                                    mapping_struct_key=mapping_struct_key)

        capnp_struct = self.__load_capnp_struct(exchange=exchange,
                                                parse_struct_key=parse_struct_key)

        capnp_message = capnp_struct.new_message()


        for json_field, capnp_field in mapping_struct.items():
            if json_field in json_data:
                setattr(capnp_message, capnp_field, json_data[json_field])

        timestamp = capnp_message.timestamp

        binary_data = capnp_message.to_bytes()
        result = self.deserialize_capnp(binary_data=binary_data,parse_struct_key=parse_struct_key)
        # print(result)
        # print(type(result))
        return timestamp, binary_data

    def upload_binary_data_to_stream(self,parse_struct_key:str,data:Any, stream_name:str,) -> None:

        try:
            if not self.redis_client.exists(stream_name):
                self.redis_client.xadd(stream_name, {"init": f"redis stream '{stream_name}' initialized."})


            create_time = self.__get_current_utc_timestamp()
            self.redis_client.xadd(stream_name,
                            {"data_type": parse_struct_key,
                                  "create_time": create_time,
                                  "binary_data": data})
            return None
        except Exception as e:
            print(e)
            return e

    # Need annotation.
    def deserialize_capnp(self, binary_data:bytes, parse_struct_key:str) -> DeserializedCapnpStruct:
        capnp_struct = self.capnp_struct[parse_struct_key]
        with capnp_struct.from_bytes(binary_data) as message:
            return message ##

    def update_parse_info(self,exchange:str, struct_key:str, struct_content:str)-> None:
        try:
            self.redis_client.hget(exchange+"_Parser",struct_key, struct_content)
            return None
        except Exception as e:
            print(e)


    def __get_current_utc_timestamp(self) -> int:
        utc_timestamp = time.time()
        utc_timestamp_ms = int(utc_timestamp * 1000000)
        return utc_timestamp_ms

    def __load_capnp_struct(self, exchange:str, parse_struct_key:str) -> CapnpStruct:
        if parse_struct_key in self.capnp_struct:
            return self.capnp_struct[parse_struct_key]
        else:
            try:
                schema_content = self.redis_client.hget(exchange + "_Parser", parse_struct_key)
                with tempfile.NamedTemporaryFile(suffix=".capnp", mode="w+", delete=True) as temp_file:
                    temp_file.write(schema_content)
                    temp_file.flush()
                    capnp_parsed_schema = capnp.load(temp_file.name)

                capnp_struct = getattr(capnp_parsed_schema, self.__capitalize_first_letter(parse_struct_key))
                self.capnp_struct[parse_struct_key] = capnp_struct
                # sync to the global_variable_manager for the consequent deserializing
                global_variable_manager.add(parse_struct_key,capnp_struct)
                return capnp_struct
            except Exception as e:
                print(e)

    def __load_mapping_struct(self, exchange:str, mapping_struct_key:str) -> dict:

        if mapping_struct_key in self.mapping_struct:
            return self.mapping_struct[mapping_struct_key]
        else:
            try:
                mapping_data = self.redis_client.hget(exchange + "_Parser", mapping_struct_key)
                if not mapping_data:
                    raise ValueError("Mapping not found in Redis.")
                else:
                    mapping_json = json.loads(mapping_data)
                    self.mapping_struct[mapping_struct_key] = mapping_json
                    return mapping_json
            except Exception as e:
                print(e)
                raise e

    def __capitalize_first_letter(self,word:str) -> str:
        return word[0].upper() + word[1:]



def test_data_parse_manager():
    test_redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    data_parse_manager = Data_Parse_Manager(redis_client=test_redis_client)
    test_exchange = "Binance"
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


    data_parse_manager.parse_json_to_binary(exchange="Binance",
                                            json_data=test_json_data,
                                            parse_struct_key="spotTickTrade",
                                            mapping_struct_key="spotTickTradeMapping"
                                            )

if __name__ == '__main__':
    test_data_parse_manager()


