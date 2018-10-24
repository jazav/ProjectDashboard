import argparse
import sys
from config_controller import *
from dashboard_controller import DashboardController
from adapters.jira_adapter import *
from dashboards.dashboard import *

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"


def get_command_namespace(argv):
    parser = argparse.ArgumentParser(description='Project Dashboards help:')

    subparsers = parser.add_subparsers(help='list of commands:', dest='command')

    init_parser = subparsers.add_parser('init', help='initialize data cache')
    # init_parser.add_argument('-filter', '-f', action="store",
    #                               help="list of filters (divided by ,): CRM,DEVPLAN,BACKLOG or possible to use the word ALL",
    #                               required=False, default="ALL")
    init_parser.add_argument('-query', '-q', action="store", help="query for jira", required=False)
    init_parser.add_argument('-jira', '-j', action="store", help="jira from config", required=False, default="jira_1")

    update_parser = subparsers.add_parser('update', help='update data cache')
    update_parser.add_argument('-start', '-s', action="store",
                               help='point to start of changes (format: 2018-08-31T14:25:21)', required=False)
    update_parser.add_argument('-query', '-q', action="store", help="query for jira", required=False)
    update_parser.add_argument('-jira', '-j', action="store", help="jira from config", required=False, default="jira_1,jira_2")

    issue_parser = subparsers.add_parser('issue', help='get issue info')
    issue_parser.add_argument('-mode', '-m', action="store", help='witch fields to show: public, technical, empty',
                              required=False)

    issue_parser.add_argument('-key', '-k', action="store", help='key of issue like BSSARBA-1203', required=True)
    issue_parser.add_argument('-export', '-e', action="store", help='export to txt,json', required=False,
                              default=EXPORT_MODE[TXT_IDX])
    issue_parser.add_argument('-jira', '-j', action="store", help="jira from config", required=False, default="jira_1")

    for subparser in [init_parser, update_parser, issue_parser]:
        subparser.add_argument('-user', '-u', action="store", help='user name of Jira account', required=True)
        subparser.add_argument('-password', '-p', action="store", help='password of Jira account', required=True)

    dashboard_parser = subparsers.add_parser('dashboard', help='show dashboard')
    dashboard_parser.add_argument('-name', '-n', action="store", help="name of dashboard", required=True)
    dashboard_parser.add_argument('-mode', '-m', action="store", help="mode to show: plan,fact", required=False,
                                  default="plan,fact")
    dashboard_parser.add_argument('-details', '-d', action="store", help="mode to show: domain|component",
                                  required=False,
                                  default="domain")
    dashboard_parser.add_argument('-export', '-e', action="store", help='export to plot', required=False,
                                  default=EXPORT_MODE[PLOT_IDX])
    dashboard_parser.add_argument('-projects', '-p', action="store",
                                  help="list of projects, to show progress (divided by ,) : BSSPAY,BSSBFAM",
                                  required=False, default="BSSPAY,BSSUFM,BSSBFAM,BSSLIS")

    name_space = parser.parse_args(args=argv)
    return name_space


def get_plan_fact(parameters):
    plan = False
    fact = False
    if parameters is None or parameters.strip() == "":
        plan = True
        fact = True
        return plan, fact

    prmt_list = parameters.split(',')
    for param in prmt_list:
        if "plan" in param:
            plan = True
        if "fact" in param:
            fact = True
    return plan, fact


def get_jira_url(jira):
    cc = cc_klass()
    options = cc.read_jira_config()
    if jira in options['servers']:
        jira_url = options['servers'][jira]
    else:
        raise Exception('{0} not found in {1}'.format(jira, cc.get_ini_path()))
    return jira_url


def main(argv):
    cc = cc_klass()
    cc.prepare_dirs()

    name_space = get_command_namespace(argv)

    print('start %s', name_space.command)
    dshc = DashboardController()

    if name_space.command in ("init", "update", "issue"):
        cc.set_login(user=name_space.user, password=name_space.password)

        if name_space.command == "init":
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = get_jira_url(jira=jira_name)
                dshc.initialize_cache(query=name_space.query, url=jira_url, jira_name=jira_name)

        if name_space.command == "update":
            # sample: 2018-08-31T14:25:21.748515
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = get_jira_url(jira=jira_name)
                dshc.update(query=name_space.query, start=name_space.start, jira_url=jira_url, jira_name=jira_name)

        if name_space.command == "issue":
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = get_jira_url(jira=jira_name)
                dshc.dashbord_issue_detail(key=name_space.key, field_mode=name_space.mode, export=name_space.export,
                                       jira_url=jira_url)
    if name_space.command == "dashboard":
        if name_space.name == "fgp":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_feature_group_progress(plan=plan, fact=fact, details=name_space.details)

        if name_space.name == "fp":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_feature_progress(plan=plan, fact=fact, details=name_space.details)

        if name_space.name == "domain":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_feature_domain_progress(plan=plan, fact=fact, details=name_space.details,
                                                   projects=name_space.projects.split(","))
        if name_space.name == "hm":
            dshc.dashboard_heatmap()


if __name__ == '__main__':
    main(sys.argv[1:])
