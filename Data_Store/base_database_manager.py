'''
@File: base_database_manager.py
@Description: ... ;
@Author: Jerry ;
@Date  : 10/2/25
Version: 1.0.0
Update Record:
-- 10/2/25: initialize version 1.0.0;
'''
import tomli
from pathlib import Path
from abc import ABC,abstractmethod
from global_manager import Global_Variable_Manager,PROJECT_ROOT
global_variable_manager = Global_Variable_Manager()


def get_database_config_info():
    folder_path = PROJECT_ROOT / "Configuration_File_Manage" / "Database_Config_Info"
    config_file_path = list(Path(folder_path).rglob(f"*.toml"))

    database_config_info = {}
    for _config_file_path in config_file_path:
        filename = _config_file_path.name
        config_info_name = filename.split(".")[0]


        with open(_config_file_path, "rb") as f:
            config_info = tomli.load(f)
            #print(config_info)
        database_config_info[config_info_name] = config_info

    #print(config_info_manager)
    return database_config_info
class Base_Database_Manager(ABC):
    #database_config_info = get_database_config_info()
    if not database_config_info:
        raise ValueError(f"fail to load database_config_info.")
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass



if __name__ == '__main__':
    get_database_config_info()