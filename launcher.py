import argparse
import sys
# from config_controller import *
from dashboard_controller import DashboardController
from adapters.jira_adapter import *
from dashboards.dashboard import *
from dashboards.feature_progress_domain_dashboard import DashboardType, DashboardFormat
import json

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"


def get_command_namespace(argv):
    parser = argparse.ArgumentParser(description='Project Dashboards help:')

    subparsers = parser.add_subparsers(help='list of commands:', dest='command')

    init_parser = subparsers.add_parser('init', help='initialize data cache')
    # init_parser.add_argument('-filter', '-f', action="store",
    #                          help="list of filters (divided by ,): CRM,DEVPLAN,BACKLOG or ALL",
    #                          required=False, default="ALL")
    init_parser.add_argument('--query', '-q', action="store", help="query for jira", required=False)
    init_parser.add_argument('--jira', '-j', action="store", help="jira from config", required=False, default="jira_1")

    update_parser = subparsers.add_parser('update', help='update data cache')
    update_parser.add_argument('--start', '-s', action="store",
                               help='point to start of changes (format: 2018-08-31T14:25:21)', required=False)
    update_parser.add_argument('--query', '-q', action="store", help="query for jira", required=False)
    update_parser.add_argument('--jira', '-j', action="store", help="jira from config", required=False,
                               default="jira_1,jira_2")

    issue_parser = subparsers.add_parser('issue', help='get issue info')
    issue_parser.add_argument('--mode', '-m', action="store", help='witch fields to show: public, technical, empty',
                              required=False)

    issue_parser.add_argument('--key', '-k', action="store", help='key of issue like BSSARBA-1203', required=True)
    issue_parser.add_argument('--export', '-e', action="store", help='export to txt,json', required=False,
                              default=EXPORT_MODE[TXT_IDX])
    issue_parser.add_argument('--jira', '-j', action="store", help="jira from config", required=False, default="jira_1")

    # loop for cache parsers
    for subparser in [init_parser, update_parser, issue_parser]:
        subparser.add_argument('--user', '-u', action="store", help='user name of Jira account', required=True)
        subparser.add_argument('--password', '-p', action="store", help='password of Jira account', required=True)

    dashboard_parser = subparsers.add_parser('dashboard', help='show dashboard')

    dashboard_parser.add_argument('--name', '-n', action="store", help="name of dashboard", required=True)

    dashboard_parser.add_argument('--mode', '-m', action="store", help="mode to show: plan,fact", required=False,
                                  default="plan,fact")

    dashboard_parser.add_argument('--details', '-d', action="store", help="mode to show: domain|component",
                                  required=False,
                                  default="domain")

    dashboard_parser.add_argument('--export', '-e', action="store", help='export to plot', required=False,
                                  default=EXPORT_MODE[PLOT_IDX])

    dashboard_parser.add_argument('--projects', '-p', action="store",
                                  help="list of projects, to show progress (divided by ,) : BSSPAY,BSSBFAM",
                                  required=False, default="")

    dashboard_parser.add_argument('--fixversion', '-f', action="store",
                                  help="fixversion : SuperSprint7",
                                  required=False, default="")

    dashboard_parser.add_argument('--sprint', '-s', action="store",
                                  help="sprint : Super Sprint 8",
                                  required=False, default="Super Sprint 8")

    dashboard_parser.add_argument('--components', '-cmp', action="store",
                                  help="components : Product Instances",
                                  required=False, default="")

    dashboard_parser.add_argument('--auto_open', '-a', action="store",
                                  help="auto_open : True",
                                  required=False, default="True")

    dashboard_parser.add_argument('--dashboard_type', '-dt', action="store",
                                  help="dashboard_type : FEATURE or PROJECT or DOMAIN",
                                  required=False, default="FEATURE")

    dashboard_parser.add_argument('--dashboard_format', '-df', action="store",
                                  help="dashboard_format : HTML or PNG",
                                  required=False, default="HTML")

    dashboard_parser.add_argument('--upload_to_file', '-uf', action='store', help='Download issues to sql file',
                                  required=False, default='False')
    
    # By @alanbryn -----------------------------------------------------------------------------------------------------
    dashboard_parser.add_argument('--priorities', '-pr', action='store', help='e.g. priority: Blocker',
                                  required=False, default="")

    dashboard_parser.add_argument('--labels', '-l', action='store', help='RnD labels field', required=False, default='')

    dashboard_parser.add_argument('--creators', '-cr', action='store', help='Creators for issues',
                                  required=False, default='')

    dashboard_parser.add_argument('--assignees', '-as', action='store', help='Assignees for issues',
                                  required=False, default='')

    dashboard_parser.add_argument('--teams', '-t', action='store', help='BSSBox teams', required=False, default='')

    dashboard_parser.add_argument('--statuses', '-st', action='store', help='Issues\' status field', required=False,
                                  default='')

    dashboard_parser.add_argument('--repository', '-rep', action='store', help='Online or offline plot saving',
                                  required=False, default='offline')

    dashboard_parser.add_argument('--mssql', action='store', help='File in SQL_queries repository',
                                  required=False, default='')

    dashboard_parser.add_argument('--citrix_token', '-ct', action='store', help='Token for Citrix ShareFile API',
                                  required=False, default='{}')

    dashboard_parser.add_argument('--local_user', '-lu', action='store', help='Local user on current PC',
                                  required=False, default='')

    dashboard_parser.add_argument('--user', action='store', help='Jira username', required=False, default='')

    dashboard_parser.add_argument('--password', action='store', help='Jira password', required=False, default='')

    dashboard_parser.add_argument('--dashboard_name', '-dn', action='store', help='Dashboard title', required=False,
                                  default='')

    dashboard_parser.add_argument('--start_date', '-sd', action='store', help='Start of work with format %d.%m.%y',
                                  required=False, default='')

    dashboard_parser.add_argument('--end_date', '-ed', action='store', help='End of work with format %d.%m.%y',
                                  required=False, default='')
    # ------------------------------------------------------------------------------------------------------------------
    
    for subparser in [init_parser, update_parser, issue_parser, dashboard_parser]:
        subparser.add_argument('--cache', '-c', action="store", help="cache file", required=False)

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


def main(argv):
    cc = cc_klass()

    name_space = get_command_namespace(argv)

    print('start {0}'.format(name_space.command))
    dshc = DashboardController()

    if name_space.cache is not None:
        cc.set_data_cache(name_space.cache)
    cc.prepare_dirs()

    if name_space.command in ("init", "update", "issue"):

        cc.set_login(user=name_space.user, password=name_space.password)

        if name_space.command == "init":
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = cc.get_jira_url(jira=jira_name)
                dshc.initialize_cache(query=name_space.query, url=jira_url, jira_name=jira_name)

        if name_space.command == "update":
            # sample: 2018-08-31T14:25:21.748515
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = cc.get_jira_url(jira=jira_name)
                dshc.update(query=name_space.query, start=name_space.start, jira_url=jira_url, jira_name=jira_name)

        if name_space.command == "issue":
            jiras = name_space.jira.split(',')
            for jira_name in jiras:
                jira_url = cc.get_jira_url(jira=jira_name)
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
                                                   projects=name_space.projects.split(","),
                                                   fixversion=name_space.fixversion,
                                                   auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                                   dashboard_type=DashboardType[name_space.dashboard_type.upper()],
                                                   dashboard_format=DashboardFormat[name_space.dashboard_format.upper()],
                                                   sprint=name_space.sprint,
                                                   components=name_space.components,
                                                   upload_to_file=(name_space.upload_to_file.upper() == 'TRUE'),
                                                   labels=name_space.labels)
        
        # By @alanbryn -------------------------------------------------------------------------------------------------
        if name_space.name == "bugs_duration":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_bugs_duration(plan=plan, fact=fact, auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                         priorities=name_space.priorities.split(","), labels=name_space.labels,
                                         creators=name_space.creators, repository=name_space.repository.lower(),
                                         citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                         local_user=name_space.local_user)

        if name_space.name == "bugs_info":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_bugs(plan=plan, fact=fact, auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                priorities=name_space.priorities.split(","), projects=name_space.projects,
                                statuses=name_space.statuses, labels=name_space.labels,
                                repository=name_space.repository.lower())

        if name_space.name == "arba":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_arba_issues(plan=plan, fact=fact, auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                       assignees=name_space.assignees, teams=name_space.teams,
                                       details=name_space.details, repository=name_space.repository.lower(),
                                       citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                       local_user=name_space.local_user)

        if name_space.name == "all_bugs":
            dshc.dashboard_all_bugs(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                    repository=name_space.repository.lower(),
                                    mssql_query_file=name_space.mssql.lower(),
                                    citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                    local_user=name_space.local_user)

        if name_space.name == "bugs_progress":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_bugs_progress(plan=plan, fact=fact, auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                         repository=name_space.repository.lower(),
                                         citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                         local_user=name_space.local_user)

        if name_space.name == "bssbox_bugs_tracking":
            dshc.dashboard_bssbox_bugs_tracking(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                                repository=name_space.repository.lower(),
                                                mssql_query_file=name_space.mssql.lower(),
                                                citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                                local_user=name_space.local_user,
                                                dashboard_name=name_space.dashboard_name)

        if name_space.name == "sprint_info":
            dshc.dashboard_sprint_info(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                       repository=name_space.repository.lower(),
                                       mssql_query_file=name_space.mssql.lower(),
                                       dashboard_type=[dt.upper().strip() for dt in name_space.dashboard_type.split(',')],
                                       citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                       local_user=name_space.local_user, dashboard_name=name_space.dashboard_name,
                                       end_date=name_space.end_date)

        if name_space.name == "iot":
            dshc.dashboard_iot(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                               repository=name_space.repository.lower(),
                               mssql_query_file=name_space.mssql.lower(),
                               citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                               local_user=name_space.local_user)

        if name_space.name == "sprint_burndown":
            dshc.dashboard_sprint_burndown(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                           repository=name_space.repository.lower(),
                                           mssql_query_file=[mssql.lower().strip() for mssql in name_space.mssql.split(',')],
                                           dashboard_type=[dt.upper().strip() for dt in name_space.dashboard_type.split(',')],
                                           citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                           local_user=name_space.local_user, dashboard_name=name_space.dashboard_name,
                                           start_date=name_space.start_date, end_date=name_space.end_date)

        if name_space.name == "yota_burndown":
            dshc.dashboard_yota_burndown(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                         repository=name_space.repository.lower(), local_user=name_space.local_user,
                                         mssql_query_file=[mssql.lower().strip() for mssql in name_space.mssql.split(',')],
                                         dashboard_type=[dt.upper().strip() for dt in name_space.dashboard_type.split(',')],
                                         citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                         labels=[lbl.strip() for lbl in name_space.labels.split(',')],
                                         dashboard_name=name_space.dashboard_name, start_date=name_space.start_date,
                                         end_date=json.loads(name_space.end_date.replace('\'', '"')))

        if name_space.name == "ba_work_distribution":
            dshc.dashboard_ba_work_distribution(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                                repository=name_space.repository.lower(),
                                                mssql_query_file=name_space.mssql.lower(),
                                                citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                                local_user=name_space.local_user)

        if name_space.name == "sprint_overview":
            dshc.dashboard_sprint_overview(auto_open=(name_space.auto_open.upper() == 'TRUE'),
                                           repository=name_space.repository.lower(), local_user=name_space.local_user,
                                           citrix_token=json.loads(name_space.citrix_token.replace('\'', '"')),
                                           user=name_space.user, password=name_space.password, sprint=name_space.sprint,
                                           start_date=name_space.start_date, end_date=name_space.end_date)
        # --------------------------------------------------------------------------------------------------------------
        # if name_space.name == "bugs_density":
        #     dshc.dashboard_bugs_density(auto_open=(name_space.auto_open.upper() == 'TRUE'),
        #                                  plotly_auth=[name_space.plotly_user, name_space.plotly_key])
        if name_space.name == "hm":
            dshc.dashboard_heatmap()


if __name__ == '__main__':
    main(sys.argv[1:])
