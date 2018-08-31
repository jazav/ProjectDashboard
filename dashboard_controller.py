import logging
from os import path
from threading import Timer

import adapters.issue_utils as iu
import config_controller
from adapters.file_cache import FileCache
from config_controller import ConfigController
from dashboards.feature_heatmap_dashboard import FeatureHeatmapDashboard
from dashboards.feature_progress_dashboard import FeatureProgressDashboard
from dashboards.prepare_feature_data import *
from data_controller import DataController

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
        initialize_logger(output_dir='./log')

    def start_updater(self):
        options = ConfigController().read_scheluler_config()
        interval = options[config_controller.INTERVAL]

        t = Timer(interval, self.update())
        t.start()
        return t

    def stop_updater(self, t):
        t.cancel()

    @staticmethod
    def initialize_cache(query=None):
        """update data in cache"""
        mng = DataController()
        mng.initialize_cache_from_jira(query)

    @staticmethod
    def update(query, start):
        """update data in cache"""
        mng = DataController()
        mng.update_cache_from_jira(query=query, start=start)

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

    def dashbord_issue_info(self, key, with_history):
        mng = DataController()
        issue = mng.get_issue(key=key, expand=with_history)
        logging.info(issue)

    def dashboard_reference_implementation(self):
        dc = DataController()
        data = dc.get_issue_pandas(query=None)

        options = ConfigController().read_dashboards_config()
        data_path = options[config_controller.FEATURE_PROGRESS_FILE]

        data_dict = data.to_dict(orient='index')
        serializable_data_dict = iu.serialize(data_dict)
        DashboardController.save_to_json(data=serializable_data_dict, file_path=data_path)

    def dashboard_heatmap(self):
        dc = DataController()
        data = dc.get_issue_pandas(query=None, expand='')

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

    def dashboard_feature_progress(self, plan, fact):
        dc = DataController()
        data = dc.get_issue_pandas(query=None, expand='')

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
            dashboard.feature_lst_on_chart = 40
            dashboard.min_tailor = 6
            dashboard.plan = plan
            dashboard.fact = fact
            dashboard.prepare(data=df2)
            dashboard.export_to_plot()

    def dashboard_feature_group_progress(self, plan, fact):
        dc = DataController()
        data = dc.get_issue_pandas(query=None, expand=None)

        dashboard = FeatureProgressDashboard()

        fg_list = FEATURE_GROUP_LIST.split(sep=';')
        dashboard.dashboard_name = "Feature Group Dashboard"
        dashboard.feature_lst_on_chart = 30
        dashboard.min_tailor = 6
        dashboard.plan = plan
        dashboard.fact = fact
        dashboard.filter_list = fg_list
        dashboard.prepare(data=data)
        dashboard.export_to_plot()
