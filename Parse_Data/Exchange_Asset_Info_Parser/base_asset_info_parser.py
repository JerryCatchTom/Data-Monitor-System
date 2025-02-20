'''
@File: base_asset_info_parser.py
@Description: provide a base-class (strategy mode) that
              compulsorily demand all subclass to implement all regulated methods ;
@Author: Jerry ;
@Date  : 23/1/25
Version: 1.0.0
Update Record:
-- 23/1/25: initialize version 1.0.0;
'''
from abc import ABC, abstractmethod
class Base_Exchange_Asset_Info_Parser(ABC):

    @abstractmethod
    def parse_data(self):
        pass

    @abstractmethod
    def parse_spot_asset_info(self):
        pass

    @abstractmethod
    def parse_swapU_asset_info(self):
        pass

    @abstractmethod
    def parse_swapC_asset_info(self):
        pass

    @abstractmethod
    def parse_deliverU_asset_info(self):
        pass
    @abstractmethod
    def parse_deliverC_asset_info(self):
        pass

    @abstractmethod
    def parse_optionU_asset_info(self):
        pass

    @abstractmethod
    def parse_optionC_asset_info(self):
        pass

if __name__ == '__main__':
    print()