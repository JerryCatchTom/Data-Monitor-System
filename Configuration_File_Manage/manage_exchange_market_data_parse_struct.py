'''
@File: manage_exchange_market_data_parse_struct.py
@Description: ... ;
@Author: Jerry ;
@Date  : 4/2/25
Version: 1.0.0
Update Record:
-- 4/2/25: initialize version 1.0.0;
'''
import tomli
import capnp
import re

from global_manager import Global_Variable_Manager,PROJECT_ROOT
global_variable_manager = Global_Variable_Manager()


class Market_Data_Parse_Info_Manager:
    def __init__(self):
        self.__support_exchange = {"binance": None}

    def load_mapping_struct(self,exchange:str,asset_type:str,request_data_type:str,**kwargs):
        if exchange not in self.__support_exchange:
            raise KeyError(f"exchange only supports {self.__support_exchange.keys()}, but receive {exchange}.")
        else:
            support_mapping_info = self.__load_market_data_mapping_struct(exchange=exchange,**kwargs)
            try:
                mapping_info = support_mapping_info[asset_type][request_data_type]
                return mapping_info
            except Exception as e:
                print(e)
                return None

    def __load_market_data_mapping_struct(self,exchange:str,**kwargs):
        mapping_struct = global_variable_manager.get(f"{exchange}_market_data_mapping_info")
        if mapping_struct:
            return mapping_struct
        else:
            __config_file_path = (PROJECT_ROOT / "Configuration_File_Manage" / "Exchange_Market_Data_Parse_Info"
                                   /f"{exchange.capitalize()}_Market_Data_Parse_Info"
                                  /f"{exchange}_market_data_mapping_info.toml")

            with open(__config_file_path, "rb") as f:
                mapping_struct = tomli.load(f)

            global_variable_manager.add(variable_name=f"{exchange}_market_data_mapping_info",
                                        variable_value=mapping_struct)
            return mapping_struct


    def load_parse_struct(self,exchange:str,asset_type:str,request_data_type:str,**kwargs):
        if exchange not in self.__support_exchange:
            raise KeyError(f"exchange only supports {self.__support_exchange.keys()}, but receive {exchange}.")

        capnp_struct = global_variable_manager.get(f"{exchange}_{asset_type}_market_data_parse_struct")
        if capnp_struct:
            try:
                parse_struct = capnp_struct[request_data_type]
                return parse_struct
            except Exception as e:
                print(e)
                return None
        else:
            try:
                config_file_path = (PROJECT_ROOT / "Configuration_File_Manage" / "Exchange_Market_Data_Parse_Info"
                                    / f"{exchange.capitalize()}_Market_Data_Parse_Info"
                                    / f"{exchange}_{asset_type}_market_data_parse_struct.capnp")
                _capnp_struct = capnp.load(str(config_file_path))


                capnp_struct = {self.__convert_camel_to_snake(struct_name): getattr(_capnp_struct, struct_name)
                               for struct_name in dir(_capnp_struct)
                               if isinstance(getattr(_capnp_struct, struct_name), capnp._StructModule)}
                #print(capnp_struct)

                global_variable_manager.add(f"{exchange}_{asset_type}_market_data_parse_struct",
                                            capnp_struct)

                parse_struct = capnp_struct[request_data_type]

                return parse_struct

            except Exception as e:
                print(e)
                return None

    def __convert_camel_to_snake(self, name: str) -> str:
        """

        """
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', name)
        return name.lower()



def test_manager():
    test_manager = Market_Data_Parse_Info_Manager()
    result = test_manager.load_parse_struct(exchange="binance",
                                            asset_type="spot",
                                            request_data_type="tick_trade")
    print(result)

if __name__ == '__main__':
    test_manager()