'''
@File: binance_asset_info_parser.py
@Description:  a specific implementation from base-class for Binance ;
@Author: Jerry ;
@Date  : 23/1/25
Version: 1.0.0
Update Record:
-- 23/1/25: initialize version 1.0.0;
'''

from Parse_Data.Exchange_Asset_Info_Parser.base_asset_info_parser import Base_Exchange_Asset_Info_Parser
from typing import Dict,List
import time
import os
from pathlib import Path
import requests
import json
class Binance_Asset_Info_Parser(Base_Exchange_Asset_Info_Parser):
    def __init__(self):
        self.__support_asset_type = ["spot"]
        self.exchange = "Binance"
        self.__support_parse_func = {"spot":self.parse_spot_asset_info,}
        self.asset_type = None

    def parse_data(self, asset_info_data:dict, asset_type:str) -> List:
        try:
            if asset_type not in self.__support_asset_type:
                raise ValueError(f"{self.exchange} excepts the support asset types={self.__support_asset_type},"
                                 f"but receive asset_type={asset_type}.")

            self.asset_type = asset_type

            parsed_asset_info_data = self.__support_parse_func[asset_type](asset_info_data)

            return parsed_asset_info_data

        except Exception as e:
            print(e)


    def parse_spot_asset_info(self,asset_info_data) -> List:

        current_time = int(time.time() * 1000)

        parsed_asset_info_data = []
        for _asset_info_data in asset_info_data["symbols"]:
            parsed_data = {}
            parsed_data['exchange'] = self.exchange
            parsed_data["symbol"] = _asset_info_data["symbol"]
            parsed_data["assetType"] = self.asset_type
            if _asset_info_data["status"] == "TRADING":
                parsed_data["tradingStatus"] = 1
            else:
                continue
            parsed_data["createTime"] = current_time
            parsed_data["updateTime"] = current_time
            parsed_data["baseAsset"] = _asset_info_data["baseAsset"]
            parsed_data["quoteAsset"] = _asset_info_data["quoteAsset"]
            parsed_data["supportOrderType"] = _asset_info_data["orderTypes"]
            parsed_data["tickSize"] = _asset_info_data["filters"][0]["tickSize"]
            parsed_data["lotSize"] = _asset_info_data["filters"][1]["stepSize"]
            parsed_data["marketLotSize"] = _asset_info_data["filters"][3]["stepSize"]
            parsed_data["minNotional"] = _asset_info_data["filters"][6]["minNotional"]

            parsed_asset_info_data.append(parsed_data)
        # print(parsed_asset_info_data)

        return parsed_asset_info_data

    def parse_swapU_asset_info(self):
        pass

    def parse_swapC_asset_info(self):
        pass

    def parse_deliverU_asset_info(self):
        pass

    def parse_deliverC_asset_info(self):
        pass

    def parse_optionC_asset_info(self):
        pass

    def parse_optionU_asset_info(self):
        pass

def asset_info_parser():
    asset_info_parser = Binance_Asset_Info_Parser()
    return asset_info_parser
def load_test_binance_spot_asset_info_data():


    project_file_path = Path(__file__).resolve().parents[2]
    test_data_file_path = project_file_path / "Test_Data" / "test_binance_spot_asset_info_data.json"



    if os.path.exists(test_data_file_path):
        with open(test_data_file_path, "r", encoding="utf-8") as json_file:
            test_data = json.load(json_file)

        return test_data
    else:
        print("No such test file.")

def temp_request_info_data():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url=url).json()

    print(response)
    print(type(response))

    project_file_path = Path(__file__).resolve().parents[2]
    test_data_file_path = project_file_path / "Test_Data" / "test_binance_spot_asset_info_data.json"

    with open(test_data_file_path, "w", encoding="utf-8") as json_file:
        json.dump(response, json_file, indent=4, ensure_ascii=False)
    print("write done.")

def test_parse_data():
    test_data = load_test_binance_spot_asset_info_data()
    test_parser = Binance_Asset_Info_Parser()
    test_parser.parse_data(asset_info_data=test_data,asset_type="spot")

if __name__ == '__main__':
    test_parse_data()