import argparse
import sys
from config_controller import *
from dashboard_controller import DashboardController

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"


def get_command(argv):
    parser = argparse.ArgumentParser(description='Great Description To Be Here')
    parser.add_argument("-c", type=str, action="store", dest='command',
                        help="command to launch")

    parser.add_argument("-p", type=str, action="store", dest='parameter',
                        help="parameters")

    parser.add_argument("-l", type=str, action="store", dest='login',
                        help="login")

    args = parser.parse_args(args=argv)

    command = args.command
    parameter = args.parameter
    login = args.login

    if command == "":
        sys.exit(2)

    return command, parameter, login


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


def get_details(parameters):
    details = DETAIL_ARR[0]

    if parameters is None or parameters.strip() == "":
        details = DETAIL_ARR[0]
        return details

    prmt_list = parameters.split(',')
    for param in prmt_list:
        if DETAIL_ARR[0] in param:
            details = DETAIL_ARR[0]
        if DETAIL_ARR[1] in param:
            details = DETAIL_ARR[1]
    return details


def get_key_wth(parameters):
    key = None
    wth = None
    if parameters is None or parameters.strip() == "":
        return key, wth

    prmt_list = parameters.split(',')
    for param in prmt_list:
        if "key" in param:
            key = param.split("=")[1]
        if "wth" in param:
            wth = param.split("=")[1]
            if wth != "None":
                wth = bool() is True
    return key, wth


def get_update_start(parameters):
    upt_start = None
    if parameters is None or parameters.strip() == "":
        return upt_start

    prmt_list = parameters.split(',')
    for param in prmt_list:
        if "start" in param:
            # sample: 2018-08-31T14:25:21.748515
            upt_start = param.split("=")[1]
    return upt_start


def main(argv):
    command, parameters, login = get_command(argv)

    #preparing ConfigController
    cc = cc_klass()
    cc.set_login(login=login)


    if command == "ini":
        dshc = DashboardController()
        dshc.initialize_cache()

    if command == "upd":
        upd_start = get_update_start(parameters=parameters)
        dshc = DashboardController()
        dshc.update(query=None, start=upd_start)

    if command == "fgp":
        plan, fact = get_plan_fact(parameters=parameters)
        details = get_details(parameters)

        dshc = DashboardController()
        dshc.dashboard_feature_group_progress(plan=plan, fact=fact, details=details)

    if command == "fp":
        plan, fact = get_plan_fact(parameters=parameters)
        details = get_details(parameters)

        dshc = DashboardController()
        dshc.dashboard_feature_progress(plan=plan, fact=fact, details=details)

    if command == "hm":
        dshc = DashboardController()
        dshc.dashboard_heatmap()

    if command == "gi":
        key, with_history = get_key_wth(parameters=parameters)

        dshc = DashboardController()
        dshc.dashbord_issue_info(key=key, with_history=with_history)


if __name__ == '__main__':
    main(sys.argv[1:])
