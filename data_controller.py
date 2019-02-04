from adapters.jira_adapter import *
from adapters.cache_adapter import CacheAdapter
import logging
import adapters.issue_utils as iu
import config_controller
from adapters.jira_adapter import HISTORY_EXPAND
from adapters.file_cache import DAY_AGE_READ_FORMAT
from datetime import datetime
import os
# import pyodbc

from adapters.sqlite_dao_issue import get_sqlite_dao


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

    def update_cache_from_jira(self, query, start, url, jira_name):
        if self._cacheable:
            old_issue_dict = self.get_issue_dict(query=query, expand=None, url=url, jira_name=jira_name)

            updated_issues = self.get_updates_by_query(query=query, expand=None, start=start, url=url, jira_name=jira_name)
            updated_issue_dict = iu.issues_to_dict(updated_issues)

            issue_dict = iu.merge_issue(issue_dict=old_issue_dict, updated_issue_dict=updated_issue_dict)
            self.save_to_cache(issue_dict)
        else:
            logging.error('cache is not supported')

        return issue_dict

    def initialize_cache_from_jira(self, query, url, jira_name):
        if self._cacheable:
            expand = EXPAND_LIST[RENDER_FIELDS_IDX] + ',' + EXPAND_LIST[NAMES_IDX] + ',' + EXPAND_LIST[
                SCHEMA_IDX] + ',' + \
                     EXPAND_LIST[EDITMETA_IDX]
            issues = self.get_issues_by_query(query=query, expand=expand, url=url, jira_name=jira_name)
            issue_dict = iu.issues_to_dict(issues)
            self.save_to_cache(issue_dict)
        else:
            logging.error('cache is not supported')

        return issue_dict

    def get_issues_by_query(self, query, expand, url, jira_name):
        jira = self._get_jira_adapter()
        issues = jira.load_all(query=query, expand=expand, url=url, jira_name=jira_name)
        return issues

    def get_issue(self, key, jira_url):
        adapter = self._get_jira_adapter()
        #this list is a most complete information
        #renderedFields,names,schema,editmeta,changelog
        expand = EXPAND_LIST[RENDER_FIELDS_IDX] + ',' + EXPAND_LIST[NAMES_IDX] + ',' + EXPAND_LIST[SCHEMA_IDX] + ',' + \
                 EXPAND_LIST[EDITMETA_IDX] + ',' + EXPAND_LIST[CHANGELOG_IDX]

        issue = adapter.load_by_key(key=key, expand=expand, url=jira_url)
        if issue is None:
            raise Exception('issue not found')
        return issue

    def get_updates_by_query(self, query, expand, start, url, jira_name):
        jira = self._get_jira_adapter()
        cache = self._get_cache_adapter().get_cache()

        cc = cc_klass()
        options = cc.read_cache_config()
        path = options[config_controller.DATA_FILE]
        path = cc.get_info_from_data(path)

        if start is None or start.strip() == "":
            age = cache.read_info(file_info=path)
        else:
            age = datetime.strptime(start, DAY_AGE_READ_FORMAT)

        logging.debug('update age from %s', age)

        if age is not None:
            issues = jira.load_updated(query=query, age=age, expand=expand, url=url, jira_name=jira_name)
        else:
            issues = self.get_issues_by_query(query, expand=expand, url=url, jira_name=jira_name)

        logging.debug('len(issues) == %s', len(issues))
        return issues

    def get_issue_dict(self, query, expand, url, jira_name):
        if self._cacheable:
            cache = self._get_cache_adapter()
            serializable_issue_dict = cache.load_all(query=query, expand=expand, url=url, jira_name=jira_name)
            issue_dict = iu.deserialize(serializable_issue_dict)
            logging.debug(len(issue_dict))
        else:
            issues = self.get_issues_by_query(query=query, expand=expand)
            issue_dict = iu.issues_to_dict(issues)
        return issue_dict

    def get_pandas_issues(self, query, expand):
        issue_dict = self.get_issue_dict(query=query, expand=expand, url='', jira_name='')
        df = iu.get_data_frame(issue_dict)
        return df

    def create_issues(self, issues):
        jira = self._get_jira_adapter()
        issues = jira.create_issue(issues)
        return issues

    def get_issue_sqllite(self, query, expand):
        issue_dict = self.get_issue_dict(query=query, expand=expand, url='', jira_name='')
        dao_issue = get_sqlite_dao()
        dao_issue.insert_issues(issue_dict)
        return dao_issue

    # By @alanbryn
    # @staticmethod
    # def get_issues_mssql(mssql_query_file):
    #     mssql_database = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
    #                                     "Server=SRV-SQL-MIRROR\\JIRAREPORT;"
    #                                     "Database=srv-jira-prod-report;"
    #                                     "uid=rndview;pwd=V2f6A8Uf")
    #
    #     path = os.path.abspath('./SQL_queries/{}.txt'.format(mssql_query_file))
    #     with open(path, 'r') as query:
    #         sql_str = query.read()
    #         cursor = mssql_database.cursor()
    #         cursor.execute(sql_str)
    #
    #     data = {}
    #     for column in cursor.description:
    #         data[column[0]] = []
    #     for row in cursor:
    #         for el, key in zip(row, data.keys()):
    #             data[key].append(el)
    #     return data
