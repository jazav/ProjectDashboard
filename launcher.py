import argparse
import sys
from config_controller import *
from dashboard_controller import DashboardController

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"


def get_command_namespace(argv):
    parser = argparse.ArgumentParser(description='Project Dashboards help:')

    subparsers = parser.add_subparsers(help='List of commands', dest='command')

    ini_parser = subparsers.add_parser('ini', help='Initialize data. This command without params.')

    update_parser = subparsers.add_parser('update', help='Update data ([-start] is date and/or time to start update). For example: update -start 2018-08-31T14:25:21')
    update_parser.add_argument('-start', action="store", help='First time data initialization', required=False)

    issue_parser = subparsers.add_parser('issue', help='Get issue info (- key is issue key for search, -history is used if update details are needed). For example: issue -key=BSSARBA-670 -history=True')
    issue_parser.add_argument('-key', action="store", help='Key to get issue', required=True)
    issue_parser.add_argument('-history', action="store", help='Update history of issue', required=False, type=bool,
                              default=False)

    for subparser in [ini_parser, update_parser, issue_parser]:
        subparser.add_argument('-user', action="store", required=True)
        subparser.add_argument('-password', action="store", required=True)

    dashboard_parser = subparsers.add_parser('dashboard', help='Show dashboard (-name is name of dashboard, -mode is plan/fact, -details can be domain or component level). For example: dashboard -name=fgp -mode=plan,fact -details=domain')
    dashboard_parser.add_argument('-name', action="store", help="Name of dashboard")
    dashboard_parser.add_argument('-mode', action="store", help="Mode to show: plan,fact", required=False,
                                  default="plan,fact")
    dashboard_parser.add_argument('-details', action="store", help="Mode to show: domain,component", required=False,
                                  default="domain")

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
    name_space = get_command_namespace(argv)

    dshc = DashboardController()

    if name_space.command in ("ini", "update", "issue"):
        cc = cc_klass()
        cc.set_login(user=name_space.user, password=name_space.password)

        if name_space.command == "ini":
            dshc.initialize_cache()

        if name_space.command == "update":
            # sample: 2018-08-31T14:25:21.748515
            dshc.update(query=None, start=name_space.start)

        if name_space.command == "issue":
            dshc.dashbord_issue_info(key=name_space.key, with_history=name_space.history)

    if name_space.command == "dashboard":
        if name_space.name == "fgp":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_feature_group_progress(plan=plan, fact=fact, details=name_space.details)

        if name_space.name == "fp":
            plan, fact = get_plan_fact(parameters=name_space.mode)
            dshc.dashboard_feature_progress(plan=plan, fact=fact, details=name_space.details)

        if name_space.name == "hm":
            dshc.dashboard_heatmap()


if __name__ == '__main__':
    main(sys.argv[1:])
