import configparser
from pathlib import Path
import os

JIRA_INI_PATH = "./"
INI_FILE = "config.ini"
JIRA_SECTION = "JIRA"
DASHBOARDS_SECTION = "DASHBOARDS"
SCHEDULER_SECTION = "SCHEDULER"
CACHE_SECTION = "CACHE"
LOG_SECTION= "LOGS"
FEATURE_PROGRESS_FILE = "feature_progress"
DATA_FILE = "data_file"
INTERVAL = "interval"
FILE_DIR = 'file_dir'
DOMAIN_IDX = 0
COMPONENT_IDX = 1
DETAIL_ARR = ['domain', 'component']
LOG_DIR='log_dir'


# Singleton/SingletonDecorator.py
class ConfigControllerDecorator:

    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


class ConfigController:

    login = None
    password = None

    def __init__(self):
        ini_path = ConfigController.get_ini_path()
        file = Path(ini_path)
        if not file.exists():
            raise FileExistsError("file %s found", ini_path)

        self.config_controller = configparser.ConfigParser()
        self.config_controller.sections()
        self.config_controller.read(ini_path)

    @staticmethod
    def create_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def prepare_dirs(self):
        dir_list = list()
        #logs
        dir_list.append(self.read_log_config()[LOG_DIR])
        #data
        dir_list.append(Path(self.read_cache_config()[DATA_FILE]))
        #files
        dir_list.append(self.read_dashboards_config()[FILE_DIR])

        for dir in dir_list:
            self.create_dir(dir)

    @staticmethod
    def get_ini_path():
        return JIRA_INI_PATH + INI_FILE

    @staticmethod
    def get_info_from_data(data_str):
        return data_str.replace(".json", ".info")

    def read_jira_config(self):

        if self.config_controller is None:
            return None

        options = {'user_name': self.login,
                   'password': self.password,
                   'server': self.config_controller[JIRA_SECTION]['server'],
                   'max_results': self.config_controller[JIRA_SECTION]['max_results'],
                   }

        return options

    def set_login(self, user, password):
        self.login = user
        self.password = password

    def read_cache_config(self):

        if self.config_controller is None:
            return None

        options = {DATA_FILE: self.config_controller[CACHE_SECTION][DATA_FILE],
                   }

        return options

    def read_dashboards_config(self):

        if self.config_controller is None:
            return None

        options = {FEATURE_PROGRESS_FILE: self.config_controller[DASHBOARDS_SECTION][FEATURE_PROGRESS_FILE],
                   FILE_DIR: self.config_controller[DASHBOARDS_SECTION][FILE_DIR],
                   }

        return options

    def read_log_config(self):

        if self.config_controller is None:
            return None

        options = {
                   LOG_DIR: self.config_controller[LOG_SECTION][LOG_DIR],
                   }

        return options

    def read_scheluler_config(self):

        if self.config_controller is None:
            return None

        options = {INTERVAL: int(self.config_controller[SCHEDULER_SECTION][INTERVAL]),
                   }

        return options

cc_klass = ConfigControllerDecorator(ConfigController)

