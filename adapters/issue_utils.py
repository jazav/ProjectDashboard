import logging
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
        'Custom Ordering': 'Custom Ordering',
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
        'Acceptance': 'Management',
        'Adapter Libraries': 'Common',
        'Analysis': 'Analysis',
        'API Management': 'Infra',
        'Billing': 'Billing',
        'Billing Arch & SA': 'Billing',
        'CAM': 'Megafon',
        'Case Management': 'CRM',
        'CCM': 'Megafon',
        'CCMP': 'Megafon',
        'Charge Events Storage': 'CES',
        'Configuration Manager': 'Common',
        'CRM Arch & SA': 'Arch & SA',
        'Custom Activation': 'Custom',
        'Custom Billing & Finances': 'Custom',
        'Custom CAM & Searching': 'Custom',
        'Custom CCM': 'Custom',
        'Custom Components': 'CRM',
        'Custom CSRP': 'Custom',
        'Custom DAPI': 'CRM',
        'Custom Datamarts': 'Custom',
        'Custom Documents': 'Custom',
        'Custom Infrastructure': 'Custom',
        'Custom Inventory': 'Custom',
        'Custom Lifecycle': 'Custom',
        'Custom OCS': 'Custom',
        'Custom Ordering': 'Ordering & PRM',
        'Custom Payments': 'Custom',
        'Custom Processes': 'Custom',
        'Custom PSC': 'Custom',
        'Customer Order': 'Ordering & PRM',
        'Default Configuration': 'Common',
        'Design': 'Design',
        'DevOps': 'DevOps',
        'DFE': 'DFE',
        'Digital API': 'CRM',
        'Documentation': 'Doc',
        'Dunning and Collection': 'Billing',
        'File Storage': 'Ordering & PRM',
        'FPM': 'Megafon',
        'GUS': 'Megafon',
        'Infra': 'Megafon',
        'Infrastructure': 'Infra',
        'Integration': 'Integration',
        'Interaction Management': 'CRM',
        'Lifecycle': 'Common',
        'LIS': 'Megafon',
        'Logical Resource Inventory': 'CRM',
        'Marketplace': 'CRM',
        'Message Bus': 'Infra',
        'Network Monetization': 'NWM',
        'Notification Engine': 'Infra',
        'OAPI': 'Megafon',
        'OM Architecture': 'Arch & SA',
        'OM System Analysis': 'Arch & SA',
        'Order Capture': 'CRM',
        'Ordering': 'Ordering & PRM',
        'Ordering Arch & SA': 'Ordering & PRM',
        'Partner Billing': 'Ordering & PRM',
        'Partner Management': 'Ordering & PRM',
        'Partner Processes': 'Ordering & PRM',
        'Partners Arch & SA': 'Ordering & PRM',
        'Party Management': 'CRM',
        'Payment Management': 'Pays',
        'Pays Arch & SA': 'Pays',
        'Performance Testing': 'Performance Testing',
        'Planning': 'Common',
        'Process Engine': 'CRM',
        'Process Management': 'CRM',
        'Product Catalog': 'Megafon',
        'Product Instances': 'Product Instances',
        'Prorate': 'Common',
        'QC Design': 'QC',
        'QC Testing': 'QC',
        'Reference Data Management': 'PSC',
        'Searching': 'CRM',
        'Security': 'Infra',
        'Shared Libraries': 'Common',
        'SSO': 'Infra',
        'System Architecture': 'System Architecture',
        'System Log': 'Infra',
        'System Monitoring and Operation': 'Infra',
        'Task Engine': 'Infra',
        'Custom NWM_OCS': 'Custom',
        'Principal Systems Architect': 'System Architecture',
        'SLS': 'Megafon',
        'Bulk Operations': 'Megafon',
        'Custom Bulk Operations': 'Custom Bulk Operations',
        'Pays_OFD': 'Megafon',
        'UNIBLP': 'Megafon',
        'Billing UI': 'Billing',
        'CRAB': 'Custom',
        'HEX': 'Custom',
        'OM Arch & SA': 'Ordering & PRM',
        '': 'Empty',
        None: 'Empty'
    }[component]


domain_shortener = {
    'Management': 'Management',
    'Common': 'Common',
    'SRS & PI Analysis': 'Analysis',
    'Infra': 'Infra',
    'Billing': 'Billing',
    'Megafon': 'Megafon',
    'CRM': 'CRM',
    'Charge Events Storage': 'CES',
    'Arch & SA': 'Arch & SA',
    'Custom Activation': 'Custom',
    'Custom Billing & Finances': 'Custom',
    'Custom CAM & Searching': 'Custom',
    'Custom CCM': 'Custom',
    'Custom CSRP': 'Custom',
    'Custom Documents/Datamarts': 'Custom',
    'Custom Infrastructure': 'Custom',
    'Custom Inventory': 'Custom',
    'Custom': 'Custom',
    'Custom OCS/PSC': 'Custom',
    'Order Management & Partner Management': 'Ordering & PRM',
    'Custom Payments': 'Custom',
    'Design': 'Design',
    'DevOps': 'DevOps',
    'DFE': 'DFE',
    'Documentation': 'Doc',
    'Integration': 'Integration',
    'Network Monetization': 'NWM',
    'Payment Management': 'Pays',
    'Performance Testing': 'Performance Testing',
    'Product Instances': 'Product Instances',
    'Quality Control': 'QC',
    'Product Management': 'PSC',
    'System Architecture': 'System Architecture',
    'Custom NWM/PSC': 'Custom',
    'Principal Systems Architect': 'System Architecture',
    'Custom Bulk Operations': 'Custom'
}


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
BULK_FIELD = 'customfield_20728'

DATETIME_WRITE_FORMAT = "{0:%Y-%m-%d %X.%f%z}"
DATETIME_READ_FORMAT = "%Y-%m-%d %X.%f%z"
DATE_WRITE_FORMAT = '{0:%Y-%m-%d}'

DATETIME_FORMAT = '%Y-%m-%dT%X.%f%z'
DATE_FORMAT = '%Y-%m-%d'
BULK_FIELD_MAPPER = {
    "41715": "Partners Arch & SA",
"42102": "PSC Configuration",
"41645": "CRM Arch & SA",
"40009": "Product Instances",
"41404": "Performance Testing",
"41711": "OM Architecture",
"40306": "Customer Order",
"41403": "QC",
"41917": "Custom Components",
"41814": "Ordering Arch & SA",
"40030": "System Log",
"40031": "Shared Libraries",
"41602": "OM System Analysis",
"42103": "NWM Configuration",
"41230": "Planning",
"40026": "Task Engine",
"40029": "System Monitoring and Operation",
"40001": "Digital API",
"40000": "DFE",
"40003": "Party Management",
"40002": "Searching",
"40005": "Case Management",
"40004": "Interaction Management",
"40007": "Process Engine",
"40028": "Notification Engine",
"40801": "Infra",
"40008": "Order Capture",
"40025": "Message Bus",
"40024": "API Management",
"40023": "Network Monetization",
"40022": "Partner Billing",
"40021": "Partner Management",
"40020": "Logical Resource Inventory",
"41405": "SSO",
"41418": "Partner Processes",
"41798": "Custom CSRP",
"41799": "Custom DAPI",
"41402": "DevOps",
"40006": "Process Management",
"40037": "Default Configuration",
"41802": "Custom PI & Marketplace",
"41803": "Custom Inventory",
"41800": "Custom Processes",
"41801": "Custom Ordering",
"41712": "Billing Arch & SA",
"41713": "Collection Arch & SA",
"41804": "Custom OCS",
"41805": "Custom Billing & Finances",
"41808": "Custom Datamarts",
"41809": "Custom Infrastructure",
"42042": "Prorate",
"40032": "Configuration Manager",
"42044": "Lifecycle",
"40019": "Payment Management",
"40012": "Service Activation",
"40027": "Security",
"41714": "Pays Arch & SA",
"41905": "Custom Party & Searching",
"40038": "Documentation",
"40013": "File Storage",
"40010": "Ordering",
"40011": "Marketplace",
"40016": "Billing",
"40017": "Dunning and Collection",
"40014": "Product Catalog",
"40015": "Reference Data Management",
"42043": "Custom Lifecycle",
"41806": "Custom Payments",
"40018": "Charge Events Storage",
"40033": "Adapter Libraries",
"40034": "Business Analysis",
"40035": "System Architecture",
"40036": "Design",
"41807": "Custom Documents",
"42349": "QC Design",
"41403": "QC Testing"
}

COMPONENT_FIELD_MAPPER = {
  "Logical Resource Inventory": "CRM1 (Customer Relationship Management)", 
  "Billing": "Billing", 
  "Ordering": "Ordering", 
  "Interaction Management": "CRM1 (Customer Relationship Management)", 
  "DevOps": "DevOps", 
  "DFE": "DFE", 
  "Custom Party & Searching": "Custom", 
  "CRM Arch & SA": "Arch & SA", 
  "Product Catalog": "Product Management", 
  "Custom DAPI": "Custom DAPI",
  "Security": "Infra", 
  "Customer Order": "Ordering", 
  "Partner Processes": "Ordering", 
  "File Storage": "Ordering", 
  "Configuration Manager": "Common", 
  "Ordering Arch & SA": "Arch & SA", 
  "Partners Arch & SA": "Arch & SA", 
  "Default Configuration": "Common", 
  "Custom Payments": "Custom", 
  "Custom Datamarts": "Custom", 
  "System Log": "Infra", 
  "Custom Processes": "Custom Processes",
  "Infra": "Infra", 
  "Network Monetization": "Network Monetization", 
  "Custom OCS": "Custom", 
  "Order Capture": "Order Capture",
  "System Architecture": "System Architecture", 
  "Party Management": "CRM1 (Customer Relationship Management)", 
  "Custom Components": "Custom Components",
  "Custom Inventory": "Custom", 
  "Custom Infrastructure": "Custom", 
  "OM Architecture": "Arch & SA", 
  "Business Analysis": "Business Analysis", 
  "Process Management": "CRM2 (Customer Relationship Management)", 
  "Service Activation": "Ordering", 
  "Performance Testing": "Performance Testing", 
  "Digital API": "Digital API",
  "Custom CSRP": "Custom", 
  "Adapter Libraries": "Common", 
  "Process Engine": "Process Engine",
  "Custom Billing & Finances": "Custom", 
  "Reference Data Management": "Product Management", 
  "Product Instances": "Product Instances", 
  "Documentation": "Documentation", 
  "API Management": "Infra", 
  "Custom Ordering": "Custom Ordering",
  "Partner Billing": "Ordering", 
  "Custom PI & Marketplace": "Custom", 
  "Custom Documents": "Custom", 
  "Message Bus": "Infra", 
  "Shared Libraries": "Common", 
  "Partner Management": "Ordering", 
  "Task Engine": "Infra", 
  "Charge Events Storage": "Charge Events Storage", 
  "Marketplace": "CRM1 (Customer Relationship Management)", 
  "System Monitoring and Operation": "Infra", 
  "OM System Analysis": "Arch & SA", 
  "Collection Arch & SA": "Arch & SA", 
  "Searching": "CRM1 (Customer Relationship Management)", 
  "Case Management": "CRM2 (Customer Relationship Management)", 
  "Notification Engine": "Infra", 
  "Billing Arch & SA": "Arch & SA", 
  "Pays Arch & SA": "Arch & SA", 
  "QC": "QC", 
  "Planning": "Common", 
  "Design": "Design", 
  "Payment Management": "Payment Management", 
  "Dunning and Collection": "Billing"
}


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

    if BULK_FIELD in fields:
        bulk_dict = fields[BULK_FIELD]
        for field_map_key in bulk_dict:
           issue_dict[component_to_store_field(field_map_key)] = bulk_dict[field_map_key]

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


def component_to_store_field(field_map_key):
    if field_map_key in BULK_FIELD_MAPPER:
        return "B_" + BULK_FIELD_MAPPER[field_map_key].replace(" ", "_").replace("&", "A")
    else:
        return "B_" + field_map_key


def component_to_bulk_field(field_map_key):
    if field_map_key in COMPONENT_FIELD_MAPPER:
        return "B_" +COMPONENT_FIELD_MAPPER[field_map_key].replace(" ", "_").replace("&", "A")
    else:
        return "B_" + field_map_key

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
        try:
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
        except:
           logging.error("Unexpected error on issue:", issue, ', error:', sys.exc_info()[0])

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
