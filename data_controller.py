from adapters.jira_adapter import JiraAdapter
from adapters.cache_adapter import CacheAdapter
import logging
import adapters.issue_utils as iu
import config_controller
from adapters.jira_adapter import HISTORY_EXPAND
from adapters.file_cache import DAY_AGE_READ_FORMAT
from datetime import datetime


class DataController:
    """It is a data model of dashboards"""

    _cacheable = None
    _cache_adapter = None
    _jira_adapter = None

    def __init__(self, cacheable=True):
        self._cacheable = cacheable

    def _get_jira_adapter(self):
        """Lazy jira initialization"""
        if self._jira_adapter is None:
            self._jira_adapter = JiraAdapter()
        return self._jira_adapter

    def _get_cache_adapter(self):
        """Lazy cache initialization"""
        if self._cache_adapter is None:
            self._cache_adapter = CacheAdapter()
        return self._cache_adapter

    def save_to_cache(self, issue_dict):
        if issue_dict is None:
            logging.warning('nothing to write to the cache')

        cache = self._get_cache_adapter()
        try:
            serializable_issue_dict = iu.serialize(issue_dict)
            cache.save_all(serializable_issue_dict)
            logging.info('cache was updated')
        except FileExistsError:
            logging.error('can not update the cache')

    def update_cache_from_jira(self, query, start):
        if self._cacheable:
            old_issue_dict = self.get_cacheable_issue_dict(query=query, expand=None)

            updated_issues = self.get_updated_issues_by_query(query=query, expand=None, start=start)
            updated_issue_dict = iu.issues_to_dict(updated_issues)

            issue_dict = iu.merge_issue(issue_dict=old_issue_dict, updated_issue_dict=updated_issue_dict)
            self.save_to_cache(issue_dict)
        else:
            logging.error('cache is not supported')

        return issue_dict

    def initialize_cache_from_jira(self, query):
        if self._cacheable:
            issues = self.get_issues_by_query(query=query, expand='')
            issue_dict = iu.issues_to_dict(issues)
            self.save_to_cache(issue_dict)
        else:
            logging.error('cache is not supported')

        return issue_dict

    def get_issues_by_query(self, query, expand):
        jira = self._get_jira_adapter()
        issues = jira.load_all(query=query, expand=expand)
        return issues

    def get_issue(self, key, expand):
        adapter = self._get_jira_adapter()
        issue = adapter.load_by_key(key=key, expand=expand)
        print(issue.raw)
        return issue

    def get_issue_history(self, key):
        issue = self.get_issue(key=key, expand=HISTORY_EXPAND)
        changelog = issue.changelog

        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    print(
                        'Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)

    def get_updated_issues_by_query(self, query, expand, start):
        jira = self._get_jira_adapter()
        cache = self._get_cache_adapter().get_cache()

        cc = config_controller.ConfigController()
        options = cc.read_cache_config()
        path = options[config_controller.DATA_FILE]
        path = cc.get_info_from_data(path)

        if start is None or start.strip() == "":
            age = cache.read_info(file_info=path)
        else:
            age = datetime.strptime(start, DAY_AGE_READ_FORMAT)

        logging.debug('update age from %s', age)

        if age is not None:
            issues = jira.load_updated(query=query, age=age, expand=expand)
        else:
            issues = self.get_issues_by_query(query, expand=expand)
        logging.debug('len(issues) == %s', len(issues))
        return issues

    def get_cacheable_issue_dict(self, query, expand):
        if self._cacheable:
            cache = self._get_cache_adapter()
            serializable_issue_dict = cache.load_all(query=query, expand=expand)
            issue_dict = iu.deserialize(serializable_issue_dict)
            logging.debug(len(issue_dict))

        else:
            issues = self.get_issues_by_query(query=query, expand=expand)
            issue_dict = iu.issues_to_dict(issues)
        return issue_dict

    def get_issue_pandas(self, query, expand):
        issue_dict = self.get_cacheable_issue_dict(query=query, expand=expand)
        df = iu.get_data_frame(issue_dict)
        return df

    def create_issues(self, issues):
        jira = self._get_jira_adapter()
        issues = jira.create_issue(issues)
        return issues
