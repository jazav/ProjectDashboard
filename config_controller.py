import configparser
from pathlib import Path
import os

import datetime

import dateutil

JIRA_INI_PATH = "./"
INI_FILE = "config.ini"
JIRA_SECTION = "JIRA"
DASHBOARDS_SECTION = "DASHBOARDS"
SCHEDULER_SECTION = "SCHEDULER"
CACHE_SECTION = "CACHE"
LOG_SECTION = "LOGS"
FEATURE_PROGRESS_FILE = "feature_progress"
DATA_FILE = "data_file"
INTERVAL = "interval"
FILE_DIR = 'file_dir'
DOMAIN_IDX = 0
COMPONENT_IDX = 1
DETAIL_ARR = ['domain', 'component']
LOG_DIR = 'log_dir'
PROJECTS_SECTION = "PROJECTS"
START = "start"
END = "end"
DISPLAY_WIDTH = "display_width"

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
    _login = None
    _password = None

    def __init__(self):
        ini_path = ConfigController.get_ini_path()
        file = Path(ini_path)
        if not file.exists():
            raise FileExistsError("file {0} not found".format(ini_path))

        self.config_controller = configparser.ConfigParser()
        self.config_controller.sections()
        self.config_controller.read(ini_path)

    @staticmethod
    def create_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def prepare_dirs(self):
        dir_list = list()
        # logs
        dir_list.append(self.read_log_config()[LOG_DIR])
        # data
        path, filename = os.path.split(self.read_cache_config()[DATA_FILE])
        dir_list.append(path)
        # files
        dir_list.append(self.read_dashboards_config()[FILE_DIR])

        for dir_item in dir_list:
            self.create_dir(dir_item)

    @staticmethod
    def get_ini_path():
        return JIRA_INI_PATH + INI_FILE

    @staticmethod
    def get_info_from_data(data_str):
        return data_str.replace(".json", ".info")

    def set_login(self, user, password):
        self._login = user
        self._password = password

    #
    # readers
    #
    def read_jira_config(self):

        if self.config_controller is None:
            return None

        item_list = list(self.config_controller._sections[JIRA_SECTION])
        servers = dict()

        for item in item_list:
            if 'jira' in item:
                servers[item] = self.config_controller[JIRA_SECTION][item]

        options = {'user_name': self._login,
                   'password': self._password,
                   'servers': servers,
                   'max_results': self.config_controller[JIRA_SECTION]['max_results'],
                   }

        return options

    def get_jira_url(self, jira):
        options = self.read_jira_config()
        if jira in options['servers']:
            jira_url = options['servers'][jira]
        else:
            raise Exception('{0} not found in {1}'.format(jira, self.get_ini_path()))
        return jira_url

    def read_cache_config(self):

        if self.config_controller is None:
            return None

        options = {DATA_FILE: self.config_controller[CACHE_SECTION][DATA_FILE],
                   }

        return options

    def set_data_cache(self, cache):
        self.config_controller[CACHE_SECTION][DATA_FILE] = cache

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

    def read_projects_config(self, jira_name):

        if self.config_controller is None:
            return None
        section = PROJECTS_SECTION
        if jira_name != None:
            section= section+'_'+jira_name.upper()
        item_list = list(self.config_controller._sections[section])
        projects = dict()

        for item in item_list:
            projects[item] = self.config_controller[section][item]
        return projects

    def read_capacity(self,project, supersprint):
        if self.config_controller is None:
            return None
        section = supersprint.upper()
        if section in self.config_controller:
            capacity = self.config_controller[section][item]
        else:
            capacity = 0
        return capacity

    def getDateTimeFromISO8601String(self,s):
        d = dateutil.parser.parse(s)
        return d

    def read_supersprint_end(self, supersprint):
        if self.config_controller is None:
            return None
        section = supersprint.upper()
        end = None
        if section in self.config_controller:
            end = self.getDateTimeFromISO8601String(self.config_controller[section][END])
        return end

    def read_supersprint_start(self, supersprint):
        if self.config_controller is None:
            return None
        if supersprint == "":
            return None
        section = supersprint.upper()
        start = None
        if section in self.config_controller:
            start = self.getDateTimeFromISO8601String(self.config_controller[section][START])
        else:
            raise ValueError('Could not find section "{0}" in config'.format(section))
        return start

    def read_supersprint_length(self, supersprint):
        if self.config_controller is None:
            return None
        section = supersprint.upper()
        length = None
        if section in self.config_controller:
            start = self.config_controller[section][START]
            end = self.config_controller[section][END]
            delta = self.getDateTimeFromISO8601String(end)- self.getDateTimeFromISO8601String(start)
            length = delta.days
        return length

    def read_display_width(self):
        if self.config_controller is None:
            return None
        width = 1980
        if DASHBOARDS_SECTION in self.config_controller:
            width = int(self.config_controller[DASHBOARDS_SECTION][DISPLAY_WIDTH])
        return width

cc_klass = ConfigControllerDecorator(ConfigController)
