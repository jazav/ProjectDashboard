import logging
from os import path
from threading import Timer
import datetime

import adapters.issue_utils as iu
import config_controller
from adapters.file_cache import FileCache
from config_controller import *
from dashboards.feature_heatmap_dashboard import FeatureHeatmapDashboard
from dashboards.feature_progress_dashboard import FeatureProgressDashboard
from dashboards.feature_progress_domain_dashboard import FeatureProgressDomainDashboard, DashboardType
from dashboards.bugs_duration_dashboard import BugsDurationDashboard  # By @alanbryn
from dashboards.arba_issues_dashboard import ArbaIssuesDashboard  # By @alanbryn
from dashboards.bugs_dashboard import BugsDashboard  # By @alanbryn
from dashboards.arba_review_dashboard import ArbaReviewDashboard  # By @alanbryn
from dashboards.all_bugs_dashboard import AllBugsDashboard  # By @alanbryn
from dashboards.bugs_progress_dashboard import BugsProgressDashboard  # By @alanbryn
from dashboards.bssbox_bugs_tracking_dashboard import BssboxBugsTrackingDashboard  # By @alanbryn
from dashboards.sprint_info_dashboard import SprintInfoDashboard  # By @alanbryn
from dashboards.feature_info_dashboard import FeatureInfoDashboard  # By @alanbryn
from dashboards.iot_dashboard import IotDashboard  # By @alanbryn
from dashboards.sprint_burndown_dashboard import SprintBurndownDashboard  # By @alanbryn
from dashboards.domain_burndown_dashboard import DomainBurndownDashboard  # By @alanbryn
from dashboards.yota_burdown_dashboard import YotaBurndownDashboard  # By @alanbryn
from dashboards.ba_work_distribution_dashboard import BaWorkDistributionDashboard  # By @alanbryn
from dashboards.yota_domain_burndown_dashboard import YotaDomainBurndownDashboard  # By @alanbryn
from dashboards.issue_detail_dashboard import IssueDetailDashboard
from dashboards.prepare_feature_data import *
from data_controller import DataController
from dashboards.dashboard import *

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"
FEATURE_GROUP_LIST = "Reference_data;Product_configuration;Inventory;User_management\security_(telco_operator's_employees,_dealers'_employees);Notification_core&configuration;Notification_management;Payment_configuration;Scratch-cards_management;Document_formatting_and_printing;(Reporting_configuration_+_Mass_printing);CRM_configuration;Client_management;Customer_360_view;Client_products_management;Financial_information_management;Mass_operations;Payments_acceptance_and_management;Order_ fullfilment;Omni-channels;Interactions;Case_management;Telco_operator_organizational_structure_management;Reporting_(preparing documents_for_printing_and_mass_printing);Policy_control;Network_integration_(mediation,_HEX);Charging&Rating;Billing_configuration;Billing;Tax;GL_Integration;Dealer_management;Interconnect&Roaming;Digital_API;Products_supported;Architecture;Miscellaneous;UI_infrastructure;SelfService;SelfService_B2B;Multibalance;OTT;Collection;Thresholds;Mediation;CTI_integration;Loyalty_management;Lifecycle"


def initialize_logger(output_dir='.'):
    # logging.config.fileConfig("logging.ini")

    logger = logging.getLogger()

    logging.basicConfig(level=logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(path.join(output_dir, 'error.log'), 'w', encoding=None, delay='true')
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(path.join(output_dir, 'all.log'), 'w')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class DashboardController:
    """This class controls all dashboards (data refresh, data preparing and etc.) """

    def __init__(self):
        cc = cc_klass()
        log_dir = cc.read_log_config()[LOG_DIR]
        initialize_logger(output_dir=log_dir)

    def start_updater(self):
        options = cc_klass().read_scheluler_config()
        interval = options[config_controller.INTERVAL]

        t = Timer(interval, self.update())
        t.start()
        return t

    def stop_updater(self, t):
        t.cancel()

    @staticmethod
    def initialize_cache(query, url, jira_name):
        """update data in cache"""
        mng = DataController()
        mng.initialize_cache_from_jira(query=query, url=url, jira_name=jira_name)

    @staticmethod
    def update(query, start, jira_url, jira_name):
        """update data in cache"""
        mng = DataController()
        mng.update_cache_from_jira(query=query, start=start, url=jira_url, jira_name=jira_name)

    @staticmethod
    def get_all(query=None):
        """update data in cache"""
        mng = DataController()
        mng.get_issues_by_query(query)

    #
    # Different dashboards are here
    #
    @staticmethod
    def save_to_json(data, file_path):
        if data is None:
            raise ValueError('data %s')

        cache = FileCache()
        cache.save(data=data, data_path=file_path)

    def dashbord_issue_detail(self, key, field_mode, export, jira_url):
        dc = DataController()
        issue = dc.get_issue(key=key, jira_url=jira_url)

        dashboard = IssueDetailDashboard()
        dashboard.dashboard_name = "{0}".format(key)
        dashboard.items_on_chart = 30
        dashboard.min_item_tail = 6
        if field_mode is not None:
            dashboard.field_mode = field_mode
        dashboard.prepare(data=issue)
        dashboard.export_to_file(export_type=export)


    def dashboard_reference_implementation(self):
        dc = DataController()
        data = dc.get_pandas_issues(query=None)

        options = cc_klass().read_dashboards_config()
        data_path = options[config_controller.FEATURE_PROGRESS_FILE]

        data_dict = data.to_dict(orient='index')
        serializable_data_dict = iu.serialize(data_dict)
        DashboardController.save_to_json(data=serializable_data_dict, file_path=data_path)

    def dashboard_heatmap(self):
        dc = DataController()
        data = dc.get_pandas_issues(query=None, expand='')

        df1 = data[data.issuetype == "Epic"]
        df2 = df1[df1["labels"].str.contains(pat="num")]
        d = df2['labels'].to_dict()

        fl = get_feature_list(d)
        fgl = get_feature_series(fl, 3)

        dashboard = FeatureHeatmapDashboard()

        for i in range(0, 1):
            dashboard.dashboard_name = i  # str(i).zfill(1)
            dashboard.prepare(data=df2)
            dashboard.export_to_plot()

    def dashboard_feature_progress(self, plan, fact, details):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data = dc.get_pandas_issues(query=None, expand=None)

        df1 = data[(data.issuetype == "Epic") | (data.issuetype == "Documentation")]
        df2 = df1[df1["labels"].str.contains(pat="num")]
        d = df2['labels'].to_dict()

        fl = get_feature_list(d)
        # fg = get_group_list(d)
        fser = get_feature_series(fl, 2)

        dashboard = FeatureProgressDashboard()

        for i in range(0, len(fser)):
            dashboard.dashboard_name = 'Feature F-{0}'.format(i)  # str(i).zfill(1)
            dashboard.filter_list = ['num{0}'.format(i)]
            dashboard.items_on_chart = 40
            dashboard.min_item_tail = 6
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.details = details

            dashboard.prepare(data=data)
            dashboard.export_to_plot()

    def dashboard_feature_group_progress(self, plan, fact, details):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data = dc.get_pandas_issues(query=None, expand=None)

        dashboard = FeatureProgressDashboard()

        #Dashbord parameters

        #filter to search epics (feature group)
        fg_list = FEATURE_GROUP_LIST.split(sep=';')
        dashboard.filter_list = fg_list

        dashboard.dashboard_name = "Feature Group Dashboard"
        dashboard.items_on_chart = 30
        dashboard.min_item_tail = 6
        dashboard.plan = plan
        dashboard.fact = fact
        dashboard.details = details

        dashboard.prepare(data=data)
        dashboard.export_to_plot()

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def dashboard_feature_domain_progress(self, plan, fact, details, projects, fixversion, auto_open, dashboard_type, dashboard_format, sprint):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data_dao = dc.get_issue_sqllite(query=None, expand=None)

        project_list = projects#["BSSPAY", "BSSUFM", "BSSBFAM", "BSSLIS"]
        for project in project_list:
            dashboard = FeatureProgressDomainDashboard()
            dashboard.dashboard_name = 'All features in ' + ((fixversion + ' ') if project == "" else project)  # str(i).zfill(1)
            dashboard.filter_list = [""]
            dashboard.items_on_chart = 40
            dashboard.min_item_tail = 6
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.details = details
            dashboard.auto_open = auto_open

            dashboard.project = project
            dashboard.fixversion = fixversion
            dashboard.dashboard_type = dashboard_type
            dashboard.dashboard_format = dashboard_format
            dashboard.sprint = sprint
            dashboard.prepare(data=data_dao)

            #lopen_list, ldev_list, lclose_list, lname_list = data_dao.get_sum_by_projects(dashboard.project, "",
            #                                                                                          fixversion)
            #for val in lname_list:
            #    dashboard.open_list, dashboard.dev_list, dashboard.close_list, dashboard.name_list
            dashboard.export_to_plot()
    
    # By @alanbryn
    @staticmethod
    def dashboard_bugs_duration(plan, fact, auto_open, priorities, labels, creators, repository, plotly_auth,
                                citrix_token, local_user):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data_dao = dc.get_issue_sqllite(query=None, expand=None)

        for priority in priorities:
            dashboard = BugsDurationDashboard()
            dashboard.dashboard_name = 'Bugs Life Cycle for '
            dashboard.items_on_chart = 10
            dashboard.min_item_tail = 5
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.plotly_auth = plotly_auth
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.priority = priority.strip()
            dashboard.creators = creators
            dashboard.labels = labels
            dashboard.prepare(data=data_dao)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_arba_issues(plan, fact, auto_open, assignees, teams, details, repository, citrix_token, local_user):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data_dao = dc.get_issue_sqllite(query=None, expand=None)

        if details == 'issues':
            dashboard = ArbaIssuesDashboard()
            dashboard.dashboard_name = teams + ' issues tracking'
            dashboard.items_on_chart = 10
            dashboard.min_item_tail = 5
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.assignees = assignees
            dashboard.prepare(data=data_dao)
            dashboard.export_to_plot()
        elif details == 'review':
            dashboard = ArbaReviewDashboard()
            dashboard.dashboard_name = teams + ' review'
            dashboard.items_on_chart = 10
            dashboard.min_item_tail = 5
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.assignees = assignees
            dashboard.prepare(data=data_dao)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_bugs(plan, fact, auto_open, priorities, projects, statuses, labels, repository, plotly_auth):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data_dao = dc.get_issue_sqllite(query=None, expand=None)

        for priority in priorities:
            dashboard = BugsDashboard()
            dashboard.dashboard_name = '{0}s in BSSBox'.format(priority.strip()) if labels == ''\
                else 'Showstoppers in BSSBox'
            dashboard.items_on_chart = 10
            dashboard.min_item_tail = 5
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.priority = priority.strip()
            dashboard.projects = projects
            dashboard.statuses = statuses
            dashboard.labels = labels
            dashboard.repository = repository
            dashboard.plotly_auth = plotly_auth
            dashboard.auto_open = auto_open
            dashboard.prepare(data=data_dao)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_all_bugs(auto_open, repository, mssql_query_file, plotly_auth, citrix_token, local_user):
        dc = DataController()
        data = dc.get_issues_mssql(mssql_query_file=mssql_query_file)

        dashboard = AllBugsDashboard()
        dashboard.dashboard_name = 'All bugs in BSSBox and Domains projects'
        dashboard.repository = repository
        dashboard.plotly_auth = plotly_auth
        dashboard.auto_open = auto_open
        dashboard.citrix_token = citrix_token
        dashboard.local_user = local_user
        dashboard.prepare(data=data)
        dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_bugs_progress(plan, fact, auto_open, repository, plotly_auth, citrix_token, local_user):
        if not (plan and fact):
            raise ValueError('both of plan and fact parameters are false')

        dc = DataController()
        data_dao = dc.get_issue_sqllite(query=None, expand=None)

        dashboard = BugsProgressDashboard()
        dashboard.dashboard_name = 'BSSBox bugs progress'
        dashboard.items_on_chart = 20
        dashboard.min_item_tail = 5
        dashboard.plan = plan
        dashboard.fact = fact
        dashboard.auto_open = auto_open
        dashboard.repository = repository
        dashboard.plotly_auth = plotly_auth
        dashboard.citrix_token = citrix_token
        dashboard.local_user = local_user
        dashboard.prepare(data=data_dao)
        dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_bssbox_bugs_tracking(auto_open, repository, mssql_query_file, plotly_auth, citrix_token, local_user):
        dc = DataController()
        data = dc.get_issues_mssql(mssql_query_file=mssql_query_file)

        dashboard = BssboxBugsTrackingDashboard()
        dashboard.dashboard_name = 'BSSBox bugs tracking'
        dashboard.auto_open = auto_open
        dashboard.repository = repository
        dashboard.plotly_auth = plotly_auth
        dashboard.citrix_token = citrix_token
        dashboard.local_user = local_user
        dashboard.prepare(data=data)
        dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_sprint_info(auto_open, repository, mssql_query_file, plotly_auth, dashboard_type, citrix_token,
                              local_user):
        dc = DataController()
        data = dc.get_issues_mssql(mssql_query_file=mssql_query_file)

        for dt in dashboard_type:
            dashboard = SprintInfoDashboard() if dt == 'DOMAIN' else FeatureInfoDashboard()
            dashboard.dashboard_name = 'Super Sprint 11'
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.plotly_auth = plotly_auth
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.prepare(data=data)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_iot(auto_open, repository, mssql_query_file, plotly_auth, citrix_token, local_user):
        dc = DataController()
        data = dc.get_issues_mssql(mssql_query_file=mssql_query_file)

        dashboard = IotDashboard()
        dashboard.dashboard_name = 'IoT Super Sprint 10'
        dashboard.auto_open = auto_open
        dashboard.repository = repository
        dashboard.plotly_auth = plotly_auth
        dashboard.citrix_token = citrix_token
        dashboard.local_user = local_user
        dashboard.prepare(data=data)
        dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_sprint_burndown(auto_open, repository, mssql_query_file, plotly_auth, dashboard_type, citrix_token,
                                  local_user):
        dc = DataController()
        data_spent = dc.get_issues_mssql(mssql_query_file=mssql_query_file[0])
        data_original = dc.get_issues_mssql(mssql_query_file=mssql_query_file[1])

        for dt in dashboard_type:
            dashboard = SprintBurndownDashboard() if dt == 'SPRINT' else DomainBurndownDashboard()
            dashboard.dashboard_name = 'Burndown for Super Sprint 11'
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.plotly_auth = plotly_auth
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.multi_prepare(data_spent=data_spent, data_original=data_original)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_yota_burndown(auto_open, repository, mssql_query_file, plotly_auth, dashboard_type, citrix_token,
                                local_user, dashboard_name, start_date, end_date):
        dc = DataController()
        data_spent = dc.get_issues_mssql(mssql_query_file=mssql_query_file[0])
        data_original = dc.get_issues_mssql(mssql_query_file=mssql_query_file[1])

        for dt in dashboard_type:
            dashboard = YotaBurndownDashboard() if dt == 'TOTAL' else YotaDomainBurndownDashboard()
            dashboard.dashboard_name = dashboard_name
            dashboard.auto_open = auto_open
            dashboard.repository = repository
            dashboard.plotly_auth = plotly_auth
            dashboard.citrix_token = citrix_token
            dashboard.local_user = local_user
            dashboard.start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y').date()
            dashboard.end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y').date()
            dashboard.multi_prepare(data_spent=data_spent, data_original=data_original)
            dashboard.export_to_plot()

    # By @alanbryn
    @staticmethod
    def dashboard_ba_work_distribution(auto_open, repository, mssql_query_file, plotly_auth, citrix_token, local_user):
        dc = DataController()
        data = dc.get_issues_mssql(mssql_query_file=mssql_query_file)

        dashboard = BaWorkDistributionDashboard()
        dashboard.dashboard_name = 'Business Analysts work distribution'
        dashboard.auto_open = auto_open
        dashboard.repository = repository
        dashboard.plotly_auth = plotly_auth
        dashboard.citrix_token = citrix_token
        dashboard.local_user = local_user
        dashboard.prepare(data=data)
        dashboard.export_to_plot()
