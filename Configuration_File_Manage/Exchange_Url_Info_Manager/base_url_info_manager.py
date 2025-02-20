'''
@File: base_url_info_manager.py
@Description: ... ;
@Author: Jerry ;
@Date  : 27/1/25
Version: 1.0.0
Update Record:
-- 27/1/25: initialize version 1.0.0;
'''


from abc import ABC,abstractmethod

class Base_Url_Info_Manager(ABC):

    @abstractmethod
    def load_request_info(self,*args,**kwargs):
        pass

class Base_Rest_Api_Manager(ABC):

    @abstractmethod
    def load_request_info(self, *args, **kwargs):
        pass


class Base_Websocket_Api_Manager(ABC):
    @abstractmethod
    def load_request_info(self, *args, **kwargs):
        pass
