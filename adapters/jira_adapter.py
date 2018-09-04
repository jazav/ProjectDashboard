from jira import JIRA
from adapters.abstract_adapter import AbstractAdapter
from adapters.jsql_builder import JSQLBuilder
from config_controller import *
import urllib3
import logging

from adapters.issue_utils import clear_issues

HISTORY_EXPAND = "changelog"


def internet_on():
    try:
        http = urllib3.HTTPConnectionPool('www.google.com')
        http.urlopen(url='http://www.google.com', timeout=1.0, method='GET')
        logging.info('network is ON')
        return True
    except urllib3.exceptions.HTTPError as err:
        logging.error('network is OFF')
        return False


class JiraAdapter(AbstractAdapter):
    _connected = False

    _user_name = None
    _password = None
    _server = None
    _max_results = 0
    _jira = None

    def __init__(self):
        options = JiraAdapter.read_jira_config()
        self._user_name = options['user_name']
        self._password = options['password']
        self._server = options['server']
        self._max_results = int(options['max_results'])

    @staticmethod
    def read_jira_config():
        cc = cc_klass()
        options = cc.read_jira_config()

        if options is None:
            options = {'user_name': 'demo.demo',
                       'password': '***',
                       'server': 'https://jira.billing.ru',
                       'max_results': 0,
                       }
        return options

    @staticmethod
    def issues_to_dict(issues, clear=True):
        issues_dict = []

        if issues is None:
            logging.warning('issues is None')
            return issues_dict

        for issue in issues:
            issues_dict.append(issue.raw)

        if clear:
            issues_dict = clear_issues(issues_dict)
        return issues_dict

    def _connect(self):
        if not self._connected:
            if self._jira is None:
                if internet_on():
                    self._jira = JIRA(server=self._server, basic_auth=(self._user_name, self._password))
                    self._connected = True
                else:
                    logging.warning('working OFFLINE')

                    self._connected = False

        return self._connected

    def load_by_query(self, query_str, expand):

        if query_str is None:
            raise ValueError('nothing to load')

        issue_objs = None
        if self._connect():
            issue_objs = self._jira.search_issues(query_str, maxResults=self._max_results, expand=expand,
                                                  json_result=False)

            # for i in range(1,total, 200):
            #  issues.append(jira.search_issues(search_query, maxResults=200, startAt=i))

        issues = JiraAdapter.issues_to_dict(issue_objs)
        logging.debug('total issues: %s', len(issues))

        return issues

    def load_by_key(self, key, expand):
        if expand is None:
            expand = ''
        if self._connect():
            issue = self._jira.issue(key, expand)
            logging.debug('loaded issue: %s', issue)
        return issue

    def get_builder(self):
        return JSQLBuilder()

    def create_issue(self, issues):

        if self._connect():
            issues = self._jira.create_issues(field_list=issues)

        return issues
