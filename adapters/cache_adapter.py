from adapters.abstract_adapter import AbstractAdapter
from adapters.file_cache import FileCache
from adapters.jsql_builder import JSQLBuilder
import config_controller


class CacheAdapter(AbstractAdapter):
    """Manager to control cache"""
    _cache = None

    def get_builder(self):
        return JSQLBuilder()

    def get_cache(self):
        if self._cache is None:
            self._cache = FileCache()
        return self._cache

    def load_by_query(self, query_str, expand, url):
        cc = config_controller.cc_klass()
        data_path = cc.read_cache_config()[config_controller.DATA_FILE]

        issue_dict = self.get_cache().read(data_path=data_path)
        # issue_dict = clear_issues(issue_dict)

        return issue_dict

    def load_by_key(self, key, expand, url):
        # read from file
        raise NotImplementedError()

        return issue

    def save_all(self, data):
        cc = config_controller.cc_klass()
        data_path = cc.read_cache_config()[config_controller.DATA_FILE]

        self.get_cache().save(data=data, data_path=data_path)
