import math
from datetime import datetime
import numpy as np
import pandas as pd
import pytz
import sys


def nat_check(nat):
    return nat is None or nat == np.datetime64('NaT') or nat is pd.NaT or (
            isinstance(nat, (int, float)) and math.isnan(nat))


def get_domain(component):
    component_to_domain = {
        'B2C Self-service': 'DFE',
        'BFAM': 'Billing',
        'Billing': 'Billing',
        'CES': 'Billing',
        'Charge Events Storage': 'Billing',
        'CRM': 'CRM',
        'CRM Processes': 'CRM',
        'Case management': 'CRM',
        'Case Management': 'CRM',
        'Collection': 'Billing',
        'CustomerOrder': 'Ordering',
        'Customer Order': 'Ordering',
        'DFE': 'DFE',
        'Fin account': 'Billing',
        'Interactions': 'CRM',
        'Inventory': 'Ordering',
        'Marketplace': 'Ordering',
        'Notification': 'Infra',
        'Party Management': 'CRM',
        'Payments': 'Billing',
        'Pays': 'Billing',
        'Processes': 'CRM',
        'Product Instances': 'Ordering',
        'Product Processes': 'CRM',
        'ProductProcess': 'CRM',
        'Report Engine': 'Infra',
        'SSO': 'Infra',
        'SPP': 'Billing',
        'Searching': 'CRM',
        'Security': 'Infra',
        'configuration': 'Component Architecture',
        'logical inventory': 'CRM',
        'Logical Inventory': 'CRM',
        'notification_managment': 'Infra',
        'oredring': 'Ordering',
        'Ordering': 'Ordering',
        'payment': 'Billing',
        'Payment': 'Billing',
        'report engine': 'Infra',
        'service activator': 'Component Architecture',
        'Product': 'Ordering',
        'Resource Instances & OMS': 'Ordering',
        'BOX': 'Documentation',
        'UFM': 'Billing',
        'Processes engine': 'CRM',
        'Process Management': 'CRM',
        'Loyalty': 'CRM',
        'CSR Portal': 'DFE',
        'Partners portal': 'DFE',
        'Common': 'DFE',
        'Admin UI': 'DFE',
        'Infra': 'Infra',
        'Message Bus': 'Infra',
        'NWM': 'NWM',
        'Network Monetization': 'NWM',
        'CRAB_AKKA': 'Ordering',
        'Partner Management': 'PRM',
        'PRM': 'PRM',
        'Product Catalog': 'PSC',
        'PSC': 'PSC',
        'psc': 'PSC',
        'RefData': 'PSC',
        'Ref. Data': 'PSC',
        'Self-Care Portal': 'DFE',
        'Payment Management': 'Billing',
        'NWM_SUP': 'NWM',
        'PRM_DATA_MANAGEMENT': 'PRM',
        'PRM_SETTLEMENT MANAGEMENT': 'PRM',
        'Payment Mangement': 'Billing',
        'DOSA': 'Ordering',
        'GUS_DB_ADAPTER': 'Billing',
        'Process Engine': 'CRM',
        'Order Capture': 'CRM',
        'Analytics': 'BA',
        'Notification Engine': 'Infra',
        'File Storage': 'Ordering',
        'Digital API': 'DFE',
        'Interaction Management': 'CRM',
        'Business Analysis': 'BA',
        'System Architecture': 'Arch',
        'OM Arch & SA': 'Arch',
        'Design': 'Design',
        'Documentation': 'Doc',
        'DevOps': 'DevOps',
        'API Management': 'Infra',
        'Dunning and Collection': 'Billing',
        'Logical Resource Inventory': 'PSC',
        'Partner Billing': 'PRM',
        'Partner Processes': 'PRM',
        'Reference Data Management': 'PSC',
        'Service Activation': 'Ordering',
        '': 'Empty',
        'CRM Arch & SA': 'CRM',
        'System Log': 'Infra',
        'System Monitoring and Operation': 'Infra',
        'Task Engine': 'Infra',
        None: None,
        'Billing Arch & SA': 'Billing',
        'Collection Arch & SA': 'Billing',
        'OM Architecture': 'Ordering',
        'OM System Analysis': 'Ordering',
        'Partners Arch & SA': 'PRM',
        'Pays Arch & SA': 'Billing'
    }
    if component in component_to_domain.keys():
        return component_to_domain[component]
    else:
        return 'Common'


def get_domain_bssbox(component):
    return {
        'Billing Arch & SA': 'Arch & SA',
        'Collection Arch & SA': 'Arch & SA',
        'CRM Arch & SA': 'Arch & SA',
        'OM Architecture': 'Arch & SA',
        'OM System Analysis': 'Arch & SA',
        'Ordering Arch & SA': 'Arch & SA',
        'Partners Arch & SA': 'Arch & SA',
        'Pays Arch & SA': 'Arch & SA',
        'Billing': 'Billing',
        'Dunning and Collection': 'Billing',
        'Business Analysis': 'BA',
        'Charge Events Storage': 'CES',
        'Adapter Libraries': 'Common',
        'Configuration Manager': 'Common',
        'Default Configuration': 'Common',
        'Planning': 'Common',
        'Shared Libraries': 'Common',
        'Interaction Management': 'CRM1',
        'Logical Resource Inventory': 'CRM1',
        'Marketplace': 'CRM1',
        'Party Management': 'CRM1',
        'Searching': 'CRM1',
        'Case Management': 'CRM2',
        'Digital API': 'CRM2',
        'Order Capture': 'CRM2',
        'Process Engine': 'CRM2',
        'Process Management': 'CRM2',
        'Custom Billing & Finances': 'Custom',
        'Custom Components': 'Custom',
        'Custom CSRP': 'Custom',
        'Custom DAPI': 'Custom',
        'Custom Datamarts': 'Custom',
        'Custom Documents': 'Custom',
        'Custom Infrastructure': 'Custom',
        'Custom Inventory': 'Custom',
        'Custom OCS': 'Custom',
        'Custom Ordering': 'Custom',
        'Custom Party & Searching': 'Custom',
        'Custom Payments': 'Custom',
        'Custom PI & Marketplace': 'Custom',
        'Custom Processes': 'Custom',
        'Design': 'Design',
        'DevOps': 'DevOps',
        'DFE': 'DFE',
        'Documentation': 'Doc',
        'API Management': 'Infra',
        'Infra': 'Infra',
        'Message Bus': 'Infra',
        'Notification Engine': 'Infra',
        'Security': 'Infra',
        'System Log': 'Infra',
        'System Monitoring and Operation': 'Infra',
        'Task Engine': 'Infra',
        'SSO': 'Infra',
        'Network Monetization': 'NWM',
        'Customer Order': 'Ordering & PRM',
        'File Storage': 'Ordering & PRM',
        'Ordering': 'Ordering & PRM',
        'Partner Billing': 'Ordering & PRM',
        'Partner Management': 'Ordering & PRM',
        'Partner Processes': 'Ordering & PRM',
        'Service Activation': 'Ordering & PRM',
        'Payment Management': 'Pays',
        'Performance Testing': 'Performance Testing',
        'Product Instances': 'Product Instances',
        'Product Catalog': 'PSC',
        'Reference Data Management': 'PSC',
        'QC': 'QC',
        'System Architecture': 'System Architecture',
        '': 'Empty',
        None: 'Empty',
    }[component]


def domain_shortener(domain):
    return {
        'Arch & SA': 'Arch & SA', 'Billing': 'Billing', 'Business Analysis': 'BA', 'Charge Events Storage': 'CES',
        'Common': 'Common', 'CRM1 (Customer Relationship Management)': 'CRM1',
        'CRM2 (Customer Relationship Management)': 'CRM2', 'Custom': 'Custom', 'Design': 'Design', 'DevOps': 'DevOps',
        'DFE': 'DFE', 'Documentation': 'Doc', 'Infra': 'Infra', 'Network Monetization': 'NWM',
        'Order Management & Partner Management': 'Ordering & PRM', 'Payment Management': 'Pays',
        'Performance Testing': 'Performance Testing', 'Product Instances': 'Product Instances',
        'Product Management': 'PSC', 'QC': 'QC', 'System Architecture': 'System Architecture'
    }[domain]


def get_domain_by_project(project):
    project_to_domain = {
        'BSSARBA': 'ARBA',
        'BSSBFAM': 'Billing',
        'BILLING': 'Billing',
        'BSSGUS': 'Billing',
        'BSSCRM': 'CRM',
        'BSSCAM': 'CRM',
        'BSSCCM': 'CRM',
        'BSSCPM': 'Ordering',
        'BSSUFM': 'Billing',
        'BSSORDER': 'Ordering',
        'BSSCRMP': 'DFE',
        'BSSDAPI': 'DFE',
        'BSSSCP': 'DFE',
        'UIKIT': 'DFE',
        'RNDDOC': 'Doc',
        'BSSLIS': 'Billing',
        'BSSPRM': 'PRM',
        'BSSPSC': 'PSC',
        'BSSPAY': 'Billing',
        'BSSBOX': 'BSSBOX',
        'NWMOCS': 'NWM',
        'GUS': 'Billing',
        'BSSINFRA': 'Infra',
        'PCCM': 'NWM',
        'NWMUDR': 'NWM',
        'NWMPCRF': 'NWM',
        'NWMAAA': 'NWM',
        'NWM': 'NWM',
        'IOTCMPRTK': 'IOT',
        'IOTCMPGF': 'IOT',
        'IOTCMP': 'IOT',
        'IOTAEP': 'IOT',
        'BSSPRMP': 'DFE',
        'CNC': 'Infra',
        'PSCPSC': 'PSC',
        'CRAB': 'Ordering',
        'SSO': 'Infra',
        None: None
    }
    if project in project_to_domain.keys():
        return project_to_domain[project]
    else:
        return 'Others'


def get_domains(components):
    component_list = components.split(',')
    domains = ""
    for component in component_list:
        component = component.strip()
        try:
            domain = get_domain(component)
        except KeyError:
            domain = component

        if len(domains) > 0:
            if domain not in domains:
                domains = domains + ',' + domain
        else:
            domains = domain
    return domains

def clear_issues(issues):
    for issue in issues:
        issue_keys = list(issue.keys())
        for issue_key in issue_keys:
            if isinstance(issue[issue_key], (dict)):
                # below are properties of Fields
                field_keys = list(issue[issue_key].keys())

                for field_key in field_keys:
                    if issue[issue_key][field_key] is None or \
                            ("components" not in field_key and
                             "assignee" not in field_key and
                             "progress" not in field_key and
                             "reporter" not in field_key and
                             "issuetype" not in field_key and
                             "aggregateprogress" not in field_key and
                             "project" not in field_key and
                             "status" not in field_key and
                             "creator" not in field_key and
                             "resolution" not in field_key and
                             "customfield" not in field_key and
                             "created" not in field_key and
                             "updated" not in field_key and
                             "summary" not in field_key and
                             "description" not in field_key and
                             "timeoriginalestimate" not in field_key and
                             "duedate" not in field_key and
                             "resolutiondate" not in field_key and
                             "components" not in field_key and
                             "timeestimate" not in field_key and
                             "timespent" not in field_key and
                             "subtasks" not in field_key and
                             "issuelinks" not in field_key and
                             "parent" not in field_key and
                             "priority" not in field_key and
                             "resolution" not in field_key and
                             "fixVersions" not in field_key

                            ):
                        del issue[issue_key][field_key]
            else:
                # property of level 1
                if issue_key not in ('key', 'id') or issue[issue_key] is None:
                    del issue[issue_key]

    return issues

field_map = {'default':{'DEVELOPER_FIELD' : 'customfield_10002',
'TESTER_FIELD' : 'customfield_10003',
'SPRINT_FIELD' : 'customfield_10200',
'EPICLINK_FIELD' : 'customfield_10201',
'EPICNAME_FIELD' : 'customfield_10204',
'STORYPOINTS_FIELD' : 'customfield_10208',
'RNDLABELS_FIELD' : 'customfield_11100',
'CLM_FIELD' : 'customfield_13200'},
'sandbox': {'DEVELOPER_FIELD': 'customfield_10204',
                         'TESTER_FIELD': 'customfield_10003',
                         'SPRINT_FIELD': 'customfield_10200',
                         'EPICLINK_FIELD': 'customfield_10002',
                         'EPICNAME_FIELD': 'customfield_10201',
                         'STORYPOINTS_FIELD': 'customfield_10208',
                         'RNDLABELS_FIELD': 'customfield_11100',
                         'CLM_FIELD': 'customfield_13200'}
             }
ID_FIELD = 'id'
KEY_FIELD = 'key'
FIELDS_FIELD = 'fields'
RENDERS_FIELD = 'renderedFields'
VERSIONED_REPR ='versionedRepresentations'
NAME_FIELD = 'name'
CREATOR_FIELD = 'creator'
DUEDATE_FIELD = 'duedate'
RESOLUTIONDATE_FIELD = 'resolutiondate'
RESOLUTION_FIELD = 'resolution'
ASSIGNEE_FIELD = 'assignee'

UPDATED_FIELD = 'updated'
CREATED_FIELD = 'created'
PROJECT_FIELD = 'project'
TYPE_FIELD = 'issuetype'
STATUS_FIELD = 'status'
COMPONENTS_FIELD = 'components'
DOMAINS_FIELD = 'domains'
TIMEORIGINALESTIMATE_FIELD = 'timeoriginalestimate'
TIMEESTIMATE_FIELD = 'timeestimate'
TIMESPENT_FIELD = 'timespent'
AGGREGATETIMEESTIMATE_FIELD = 'aggregatetimeestimate'
AGGREGATETIMEORIGINALESTIMATE_FIELD = 'aggregatetimeoriginalestimate'
SUBTASKS_FIELD = 'subtasks'
SUMMARY_FIELD = 'summary'
DESCRIPTION_FIELD = 'description'
PARENT_FIELD = 'parent'
ISSUELINKS_FIELD = 'issuelinks'
REPORTER_FIELD = 'reporter'
PRIORITY_FIELD = 'priority'
AGGREGATEPROGRESS_FIELD = 'aggregateprogress'
PROGRESS_FIELD = 'progress'
FIXVERSIONS_FIELD = 'fixVersions'
PARENT_LINK_FIELD = 'customfield_20727'

DATETIME_WRITE_FORMAT = "{0:%Y-%m-%d %X.%f%z}"
DATETIME_READ_FORMAT = "%Y-%m-%d %X.%f%z"
DATE_WRITE_FORMAT = '{0:%Y-%m-%d}'

DATETIME_FORMAT = '%Y-%m-%dT%X.%f%z'
DATE_FORMAT = '%Y-%m-%d'


# def add_fields(issue, issue_dict):
#     if FIELDS_FIELD not in issue:
#         return issue_dict
#
#     if CREATOR_FIELD in issue[FIELDS_FIELD]:
#         creator = issue[FIELDS_FIELD][CREATOR_FIELD][NAME_FIELD]
#     else:
#         creator = ''
#
#     if ASSIGNEE_FIELD in issue[FIELDS_FIELD]:
#         assignee = issue[FIELDS_FIELD][ASSIGNEE_FIELD][NAME_FIELD]
#     else:
#         assignee = ''
#
#     if REPORTER_FIELD in issue[FIELDS_FIELD]:
#         reporter = issue[FIELDS_FIELD][REPORTER_FIELD][NAME_FIELD]
#     else:
#         reporter = ''
#
#     if RESOLUTIONDATE_FIELD in issue[FIELDS_FIELD]:
#         resolutiondate = datetime.strptime(issue[FIELDS_FIELD][RESOLUTIONDATE_FIELD], DATETIME_FORMAT)
#     else:
#         resolutiondate = None
#
#     if RESOLUTION_FIELD in issue[FIELDS_FIELD]:
#         resolution = issue[FIELDS_FIELD][RESOLUTION_FIELD][NAME_FIELD]
#     else:
#         resolution = ''
#
#     if DUEDATE_FIELD in issue[FIELDS_FIELD]:
#
#         duedate = datetime.strptime(issue[FIELDS_FIELD][DUEDATE_FIELD], DATE_FORMAT)
#         # it's timezone unaware
#
#         duedate = pytz.utc.localize(duedate)
#         # noew it's TZ aware
#     else:
#         duedate = None
#
#     if UPDATED_FIELD in issue[FIELDS_FIELD]:
#         updated = datetime.strptime(issue[FIELDS_FIELD][UPDATED_FIELD], DATETIME_FORMAT)
#     else:
#         updated = None
#
#     if CREATED_FIELD in issue[FIELDS_FIELD]:
#         created = datetime.strptime(issue[FIELDS_FIELD][CREATED_FIELD], DATETIME_FORMAT)
#     else:
#         created = None
#
#     if PROJECT_FIELD in issue[FIELDS_FIELD]:
#         project = issue[FIELDS_FIELD][PROJECT_FIELD][KEY_FIELD]
#     else:
#         project = ''
#
#     if PARENT_FIELD in issue[FIELDS_FIELD]:
#         parent = issue[FIELDS_FIELD][PARENT_FIELD][KEY_FIELD]
#     else:
#         parent = ''
#
#     if TYPE_FIELD in issue[FIELDS_FIELD]:
#         issuetype = issue[FIELDS_FIELD][TYPE_FIELD][NAME_FIELD]
#     else:
#         issuetype = ''
#
#     if STATUS_FIELD in issue[FIELDS_FIELD]:
#         status = issue[FIELDS_FIELD][STATUS_FIELD][NAME_FIELD]
#     else:
#         status = ''
#
#     if COMPONENTS_FIELD in issue[FIELDS_FIELD]:
#         components = ''
#         lenght = len(issue[FIELDS_FIELD][COMPONENTS_FIELD])
#         for i in range(lenght):
#             components = components + issue[FIELDS_FIELD][COMPONENTS_FIELD][i][NAME_FIELD]
#             if i < lenght - 1:
#                 components = components + ','
#     else:
#         components = ''
#
#     domains = get_domains(components)
#
#     if ISSUELINKS_FIELD in issue[FIELDS_FIELD]:
#         outwards = ''
#         inwards = ''
#         lenght = len(issue[FIELDS_FIELD][ISSUELINKS_FIELD])
#         for i in range(lenght):
#             if 'outwardIssue' in issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]:
#                 if len(outwards) > 0:
#                     outwards = outwards + ','
#                 outwards = outwards + issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]['outwardIssue'][KEY_FIELD]
#             else:
#                 if len(inwards) > 0:
#                     inwards = inwards + ','
#                 inwards = inwards + issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]['inwardIssue'][KEY_FIELD]
#     else:
#         outwards = ''
#         inwards = ''
#
#     if PRIORITY_FIELD in issue[FIELDS_FIELD]:
#         priority = issue[FIELDS_FIELD][PRIORITY_FIELD][NAME_FIELD]
#     else:
#         priority = ''
#
#     if LABEL_FIELD in issue[FIELDS_FIELD]:
#         labels = ','.join(issue[FIELDS_FIELD][LABEL_FIELD])
#     else:
#         labels = ''
#
#     if SUBTASKS_FIELD in issue[FIELDS_FIELD]:
#         subtasks = ''
#         lenght = len(issue[FIELDS_FIELD][SUBTASKS_FIELD])
#         for i in range(lenght):
#             subtasks = subtasks + issue[FIELDS_FIELD][SUBTASKS_FIELD][i][KEY_FIELD]
#             if i < lenght - 1:
#                 subtasks = subtasks + ','
#     else:
#         subtasks = ''
#
#     if TIMEORIGINALESTIMATE_FIELD in issue[FIELDS_FIELD]:
#         timeoriginalestimate = float(issue[FIELDS_FIELD][TIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
#     else:
#         timeoriginalestimate = 0.00
#
#     if STORYPOINTS_FIELD in issue[FIELDS_FIELD]:
#         storypoints = float(issue[FIELDS_FIELD][STORYPOINTS_FIELD])
#     else:
#         storypoints = 0.00
#
#     if EPICLINK_FIELD in issue[FIELDS_FIELD]:
#         epiclink = issue[FIELDS_FIELD][EPICLINK_FIELD]
#     else:
#         epiclink = ''
#
#     if TIMEESTIMATE_FIELD in issue[FIELDS_FIELD]:
#         timeestimate = issue[FIELDS_FIELD][TIMEESTIMATE_FIELD] / 60 / 60 / 8  # sec->man-days
#     else:
#         timeestimate = 0.00
#
#     if TIMESPENT_FIELD in issue[FIELDS_FIELD]:
#         timespent = float(issue[FIELDS_FIELD][TIMESPENT_FIELD] / 60 / 60 / 8)  # sec->man-days
#     else:
#         timespent = 0.00
#
#     if AGGREGATETIMEESTIMATE_FIELD in issue[FIELDS_FIELD]:
#         aggregatetimeestimate = float(
#             issue[FIELDS_FIELD][AGGREGATETIMEESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
#     else:
#         aggregatetimeestimate = 0.00
#
#     if AGGREGATEPROGRESS_FIELD in issue[FIELDS_FIELD] and 'percent' in issue[FIELDS_FIELD][AGGREGATEPROGRESS_FIELD]:
#         aggregateprogress = float(issue[FIELDS_FIELD][AGGREGATEPROGRESS_FIELD]['percent'])
#     else:
#         aggregateprogress = 0.00
#
#     if PROGRESS_FIELD in issue[FIELDS_FIELD] and 'percent' in issue[FIELDS_FIELD][PROGRESS_FIELD]:
#         progress = float(issue[FIELDS_FIELD][PROGRESS_FIELD]['percent'])
#     else:
#         progress = 0.00
#
#     if AGGREGATETIMEORIGINALESTIMATE_FIELD in issue[FIELDS_FIELD]:
#         aggregatetimeoriginalestimate = float(issue[FIELDS_FIELD][
#                                                   AGGREGATETIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
#     else:
#         aggregatetimeoriginalestimate = 0.00
#
#     if SUMMARY_FIELD in issue[FIELDS_FIELD]:
#         summary = issue[FIELDS_FIELD][SUMMARY_FIELD]
#     else:
#         summary = ''
#
#     if DESCRIPTION_FIELD in issue[FIELDS_FIELD]:
#         description = issue[FIELDS_FIELD][DESCRIPTION_FIELD]
#     else:
#         description = ''
#
#     issue_dict = {
#         TYPE_FIELD: issuetype,
#         STATUS_FIELD: status,
#         PROJECT_FIELD: project,
#         COMPONENTS_FIELD: components,
#         DOMAINS_FIELD: domains,
#         'labels': labels,
#         'epiclink': epiclink,
#         PARENT_FIELD: parent,
#         SUBTASKS_FIELD: subtasks,
#         'outwards': outwards,
#         'inwards': inwards,
#         SUMMARY_FIELD: summary,
#         DESCRIPTION_FIELD: description,
#         RESOLUTION_FIELD: resolution,
#         RESOLUTIONDATE_FIELD: resolutiondate,
#         TIMEORIGINALESTIMATE_FIELD: timeoriginalestimate,
#         TIMEESTIMATE_FIELD: timeestimate,
#         TIMESPENT_FIELD: timespent,
#         'storypoints': storypoints,
#         CREATOR_FIELD: creator,
#         ASSIGNEE_FIELD: assignee,
#         REPORTER_FIELD: reporter,
#         DUEDATE_FIELD: duedate,
#         AGGREGATETIMEESTIMATE_FIELD: aggregatetimeestimate,
#         AGGREGATETIMEORIGINALESTIMATE_FIELD: aggregatetimeoriginalestimate,
#         UPDATED_FIELD: updated,
#         CREATED_FIELD: created,
#         PROGRESS_FIELD: progress,
#         AGGREGATEPROGRESS_FIELD: aggregateprogress,
#         PRIORITY_FIELD: priority}
#
#     return issue_dict

def add_fields(fields, issue_dict):
    jira_type = 'default'
    if 'project' in fields and 'sandbox' in fields['project']['self']:
        jira_type = 'sandbox'

    if fields is None:
        return issue_dict

    if CREATOR_FIELD in fields:
        creator = fields[CREATOR_FIELD][NAME_FIELD]
    else:
        creator = ''

    if ASSIGNEE_FIELD in fields:
        assignee = fields[ASSIGNEE_FIELD][NAME_FIELD]
    else:
        assignee = ''

    if REPORTER_FIELD in fields:
        reporter = fields[REPORTER_FIELD][NAME_FIELD]
    else:
        reporter = ''

    resolutiondate = None
    try:
        if RESOLUTIONDATE_FIELD in fields:
            resolutiondate = datetime.strptime(fields[RESOLUTIONDATE_FIELD], DATETIME_FORMAT)
    except:
       print("Unexpected conver time error on issue_dict:", issue_dict, ' resolutiondate :  ', fields[RESOLUTIONDATE_FIELD], ', error:', sys.exc_info()[0])

    if RESOLUTION_FIELD in fields:
        resolution = fields[RESOLUTION_FIELD][NAME_FIELD]
    else:
        resolution = ''

    if DUEDATE_FIELD in fields:
        duedate = datetime.strptime(fields[DUEDATE_FIELD], DATE_FORMAT)
        # it's timezone unaware

        duedate = pytz.utc.localize(duedate)
        # now it's TZ aware
    else:
        duedate = None
    updated = None
    try:
        if UPDATED_FIELD in fields:
            updated = datetime.strptime(fields[UPDATED_FIELD], DATETIME_FORMAT)
    except:
       print("Unexpected conver time error on issue_dict:", issue_dict, ' update :  ', fields[UPDATED_FIELD], ', error:', sys.exc_info()[0])

    created = None
    try:
        if CREATED_FIELD in fields:
            created = datetime.strptime(fields[CREATED_FIELD], DATETIME_FORMAT)
    except:
       print("Unexpected conver time error on issue_dict:", issue_dict, ' created :  ', fields[CREATED_FIELD], ', error:', sys.exc_info()[0])

    if PROJECT_FIELD in fields:
        project = fields[PROJECT_FIELD][KEY_FIELD]
    else:
        project = ''

    if PARENT_FIELD in fields:
        parent = fields[PARENT_FIELD][KEY_FIELD]
    else:
        parent = ''

    if TYPE_FIELD in fields:
        issuetype = fields[TYPE_FIELD][NAME_FIELD]
    else:
        issuetype = ''

    if STATUS_FIELD in fields:
        status = fields[STATUS_FIELD][NAME_FIELD]
    else:
        status = ''

    if COMPONENTS_FIELD in fields:
        components = ''
        lenght = len(fields[COMPONENTS_FIELD])
        for i in range(lenght):
            components = components + fields[COMPONENTS_FIELD][i][NAME_FIELD]
            if i < lenght - 1:
                components = components + ','
    else:
        components = ''

    domains = get_domains(components)

    if ISSUELINKS_FIELD in fields:
        outwards = ''
        inwards = ''
        lenght = len(fields[ISSUELINKS_FIELD])
        for i in range(lenght):
            if 'outwardIssue' in fields[ISSUELINKS_FIELD][i]:
                if len(outwards) > 0:
                    outwards = outwards + ','
                outwards = outwards + fields[ISSUELINKS_FIELD][i]['outwardIssue'][KEY_FIELD]
            else:
                if len(inwards) > 0:
                    inwards = inwards + ','
                inwards = inwards + fields[ISSUELINKS_FIELD][i]['inwardIssue'][KEY_FIELD]
    else:
        outwards = ''
        inwards = ''

    if PRIORITY_FIELD in fields:
        priority = fields[PRIORITY_FIELD][NAME_FIELD]
    else:
        priority = ''

    if field_map[jira_type]['RNDLABELS_FIELD'] in fields:
        labels = ','.join(fields[field_map[jira_type]['RNDLABELS_FIELD']])
    else:
        labels = ''

    if SUBTASKS_FIELD in fields:
        subtasks = ''
        lenght = len(fields[SUBTASKS_FIELD])
        for i in range(lenght):
            subtasks = subtasks + fields[SUBTASKS_FIELD][i][KEY_FIELD]
            if i < lenght - 1:
                subtasks = subtasks + ','
    else:
        subtasks = ''

    if TIMEORIGINALESTIMATE_FIELD in fields:
        timeoriginalestimate = float(fields[TIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
    else:
        timeoriginalestimate = 0.00

    if field_map[jira_type]['STORYPOINTS_FIELD'] in fields:
        storypoints = float(fields[field_map[jira_type]['STORYPOINTS_FIELD']])
    else:
        storypoints = 0.00

    if field_map[jira_type]['EPICLINK_FIELD']  in fields:
        epiclink = fields[field_map[jira_type]['EPICLINK_FIELD']]
    else:
        epiclink = ''

    if field_map[jira_type]['SPRINT_FIELD']  in fields:
        sprint_class = fields[field_map[jira_type]['SPRINT_FIELD']]
        slices = sprint_class[0].split(",")
        sprint = ''
        for slice in slices:
            if slice.find('name=')==0 :
                values = slice.split("=")
                if (len(values)>1):
                    sprint = values[1]
    else:
        sprint = ''

    if TIMEESTIMATE_FIELD in fields:
        timeestimate = fields[TIMEESTIMATE_FIELD] / 60 / 60 / 8  # sec->man-days
    else:
        timeestimate = 0.00

    if TIMESPENT_FIELD in fields:
        timespent = float(fields[TIMESPENT_FIELD] / 60 / 60 / 8)  # sec->man-days
    else:
        timespent = 0.00

    if AGGREGATETIMEESTIMATE_FIELD in fields:
        aggregatetimeestimate = float(
            fields[AGGREGATETIMEESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
    else:
        aggregatetimeestimate = 0.00

    if AGGREGATEPROGRESS_FIELD in fields and 'percent' in fields[AGGREGATEPROGRESS_FIELD]:
        aggregateprogress = float(fields[AGGREGATEPROGRESS_FIELD]['percent'])
    else:
        aggregateprogress = 0.00

    if PROGRESS_FIELD in fields and 'percent' in fields[PROGRESS_FIELD]:
        progress = float(fields[PROGRESS_FIELD]['percent'])
    else:
        progress = 0.00

    if AGGREGATETIMEORIGINALESTIMATE_FIELD in fields:
        aggregatetimeoriginalestimate = float(fields[
                                                  AGGREGATETIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
    else:
        aggregatetimeoriginalestimate = 0.00

    if SUMMARY_FIELD in fields:
        summary = fields[SUMMARY_FIELD]
    else:
        summary = ''

    if DESCRIPTION_FIELD in fields:
        description = fields[DESCRIPTION_FIELD]
    else:
        description = ''
    fixversions  = ''
    if FIXVERSIONS_FIELD in fields:
        for ver in fields[FIXVERSIONS_FIELD]:
            if fixversions != '':
                fixversions = fixversions + ','
            fixversions = fixversions + ver['name']
    if PARENT_LINK_FIELD in fields:
        parent_link = fields[PARENT_LINK_FIELD]
    else:
        parent_link = ''

    issue_dict[TYPE_FIELD] = issuetype
    issue_dict[STATUS_FIELD] = status
    issue_dict[PROJECT_FIELD] = project
    issue_dict[COMPONENTS_FIELD] = components
    issue_dict[DOMAINS_FIELD] = domains
    issue_dict['labels'] = labels
    issue_dict['epiclink'] = epiclink
    issue_dict['sprint'] = sprint
    if parent_link == '':
        issue_dict[PARENT_FIELD] = parent
    else:
        issue_dict[PARENT_FIELD] = parent_link
    issue_dict[SUBTASKS_FIELD] = subtasks
    issue_dict['outwards'] = outwards
    issue_dict['inwards'] = inwards
    issue_dict[SUMMARY_FIELD] = summary
    issue_dict[DESCRIPTION_FIELD] = description
    issue_dict[RESOLUTION_FIELD] = resolution
    issue_dict[RESOLUTIONDATE_FIELD] = resolutiondate
    issue_dict[TIMEORIGINALESTIMATE_FIELD] = timeoriginalestimate
    issue_dict[TIMEESTIMATE_FIELD] = timeestimate
    issue_dict[TIMESPENT_FIELD] = timespent
    issue_dict['storypoints'] = storypoints
    issue_dict[CREATOR_FIELD] = creator
    issue_dict[ASSIGNEE_FIELD] = assignee
    issue_dict[REPORTER_FIELD] = reporter
    issue_dict[DUEDATE_FIELD] = duedate
    issue_dict[AGGREGATETIMEESTIMATE_FIELD] = aggregatetimeestimate,
    issue_dict[AGGREGATETIMEORIGINALESTIMATE_FIELD] = aggregatetimeoriginalestimate
    issue_dict[UPDATED_FIELD] = updated
    issue_dict[CREATED_FIELD] = created
    issue_dict[PROGRESS_FIELD] = progress
    issue_dict[AGGREGATEPROGRESS_FIELD] = aggregateprogress
    issue_dict[PRIORITY_FIELD] = priority
    issue_dict['fixversions'] = fixversions

    return issue_dict

def add_render_fields(fields, issue_dict):
    # if FIXVERSIONS_FIELD in fields:
    #     fixVersions = fields[FIXVERSIONS_FIELD]
    # else:
    #     fixVersions = ''
    # issue_dict['fixversions'] = fixVersions

    return issue_dict

def issues_to_dict(issues):
    issues_dict = dict()

    if issues is None or len(issues) == 0:
        return issues_dict

    for issue in issues:
        id = int(issue[ID_FIELD])
        key = issue[KEY_FIELD]

        issue_dict = {
            KEY_FIELD: key,
            ID_FIELD: id}

        if FIELDS_FIELD in issue:
            issue_dict = add_fields(fields=issue[FIELDS_FIELD], issue_dict=issue_dict)

        if VERSIONED_REPR in issue:
            issue_dict = add_fields(fields=issue[VERSIONED_REPR], issue_dict=issue_dict)

        if RENDERS_FIELD in issue:
            issue_dict = add_render_fields(fields=issue[RENDERS_FIELD], issue_dict=issue_dict)
        issues_dict[key] = issue_dict

    return issues_dict


def serialize(issue_dict):

    if issue_dict is None or len(issue_dict) == 0:
        return issue_dict

    for issue in issue_dict.values():

        if RESOLUTIONDATE_FIELD in issue:
            if nat_check(issue[RESOLUTIONDATE_FIELD]):
                issue[RESOLUTIONDATE_FIELD] = None
            else:
                issue[RESOLUTIONDATE_FIELD] = DATETIME_WRITE_FORMAT.format(issue[RESOLUTIONDATE_FIELD])

        if DUEDATE_FIELD in issue:
            if nat_check(issue[DUEDATE_FIELD]):
                issue[DUEDATE_FIELD] = None
            else:
                issue[DUEDATE_FIELD] = DATETIME_WRITE_FORMAT.format(issue[DUEDATE_FIELD])

        if UPDATED_FIELD in issue:
            if nat_check(issue[UPDATED_FIELD]):
                issue[UPDATED_FIELD] = None
            else:
                issue[UPDATED_FIELD] = DATETIME_WRITE_FORMAT.format(issue[UPDATED_FIELD])

        if CREATED_FIELD in issue:
            if nat_check(issue[CREATED_FIELD]):
                issue[CREATED_FIELD] = None
            else:
                issue[CREATED_FIELD] = DATETIME_WRITE_FORMAT.format(issue[CREATED_FIELD])

        #
        # if something is missed, we are trying to cast datetime fields
        #

        for k, v in issue.items():
            if type(v) == datetime:
                if nat_check(v):
                    issue[k] = None
                else:
                    issue[k] = DATETIME_WRITE_FORMAT.format(v)
    return issue_dict


def deserialize(issue_dict):
    if issue_dict is not None and len(issue_dict) > 0:
        for issue in issue_dict.values():

            if issue[RESOLUTIONDATE_FIELD] is not None:
                issue[RESOLUTIONDATE_FIELD] = datetime.strptime(issue[RESOLUTIONDATE_FIELD], DATETIME_READ_FORMAT)

            if issue[DUEDATE_FIELD] is not None:
                issue[DUEDATE_FIELD] = datetime.strptime(issue[DUEDATE_FIELD], DATETIME_READ_FORMAT)
                # DATE_FORMAT

            if issue[UPDATED_FIELD] is not None:
                issue[UPDATED_FIELD] = datetime.strptime(issue[UPDATED_FIELD], DATETIME_READ_FORMAT)

            if issue[CREATED_FIELD] is not None:
                issue[CREATED_FIELD] = datetime.strptime(issue[CREATED_FIELD], DATETIME_READ_FORMAT)
    return issue_dict


def merge_issue(issue_dict, updated_issue_dict):
    if updated_issue_dict is not None and len(updated_issue_dict) > 0:
        if issue_dict is None or len(issue_dict) == 0:
            issue_dict = updated_issue_dict
        else:
            for key, value in updated_issue_dict.items():
                issue_dict[key] = value
    return issue_dict


def get_data_frame(issue_dict):
    df = pd.DataFrame.from_dict(issue_dict, orient='index')
    return df
