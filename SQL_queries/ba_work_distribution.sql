WITH us AS (
	SELECT DESTINATION, (CASE WHEN us_sprint.Sprint IS NULL THEN 'Backlog' ELSE us_sprint.Sprint END) AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS us_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS us_it ON us_it.ID = us_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS us_prj ON us_prj.ID = us_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS us_il ON us_il.SOURCE = us_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS us_ilt ON us_ilt.ID = us_il.LINKTYPE
		LEFT JOIN (
			SELECT us_cfv.ISSUE,
				(CASE
					WHEN us_cfv.STRINGVALUE = '6977' THEN 'Super Sprint 6'
					WHEN us_cfv.STRINGVALUE IN ('6978', '6494') THEN 'Super Sprint 7'
					WHEN us_cfv.STRINGVALUE = '6979' THEN 'Super Sprint 7.1'
					WHEN us_cfv.STRINGVALUE = '6980' THEN 'Super Sprint 8'
					WHEN us_cfv.STRINGVALUE = '6981' THEN 'Super Sprint 8 candidates'
					WHEN us_cfv.STRINGVALUE = '6982' THEN 'Super Sprint 9 candidates'
					WHEN us_cfv.STRINGVALUE = '6983' THEN 'Super Sprint 10 candidates'
					WHEN us_cfv.STRINGVALUE = '7067' THEN 'Super Sprint 9'
					WHEN us_cfv.STRINGVALUE = '7198' THEN 'Super Sprint 10'
					WHEN us_cfv.STRINGVALUE = '7199' THEN 'Super Sprint 11 fact'
					WHEN us_cfv.STRINGVALUE = '7532' THEN 'SS11 plan'
					WHEN us_cfv.STRINGVALUE = '7326' THEN 'Super Sprint 12 fact'
					WHEN us_cfv.STRINGVALUE = '7533' THEN 'SS12 plan'
					WHEN us_cfv.STRINGVALUE = '7327' THEN 'Super Sprint 13 fact'
					WHEN us_cfv.STRINGVALUE = '7534' THEN 'SS13 plan'
					WHEN us_cfv.STRINGVALUE = '7328' THEN 'Super Sprint 14 fact'
					WHEN us_cfv.STRINGVALUE = '7535' THEN 'SS14 plan'
					WHEN us_cfv.STRINGVALUE = '7531' THEN 'Super Sprint 15 fact'
					WHEN us_cfv.STRINGVALUE = '7536' THEN 'SS15 plan'
					WHEN us_cfv.STRINGVALUE = '7329' THEN 'Out of Yota scope'
					ELSE us_cfv.STRINGVALUE
				END) AS 'Sprint'
			FROM [srv-jira-prod-report].[dbo].[customfieldvalue] us_cfv
				INNER JOIN [srv-jira-prod-report].[dbo].[customfield] AS us_cf ON us_cf.ID = us_cfv.CUSTOMFIELD
			WHERE us_cf.cfname = 'Sprint') AS us_sprint ON us_sprint.ISSUE = us_ji.ID
	WHERE us_ilt.LINKNAME = 'nexign_hierarchy_link'),
epics AS (
	SELECT e_ji.ID, e_prj.pkey AS 'Project', ec.Component, (CASE WHEN us.Sprint IS NULL THEN 'Out of Workflow' ELSE us.Sprint END) AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS e_it ON e_it.ID = e_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS e_prj ON e_prj.ID = e_ji.PROJECT
		LEFT JOIN (
			SELECT ec_ji.ID, ec_cmp.cname AS 'Component'
			FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ec_ji
				INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS ec_na ON ec_na.SOURCE_NODE_ID = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[component] AS ec_cmp ON ec_cmp.ID = ec_na.SINK_NODE_ID
			WHERE ec_na.ASSOCIATION_TYPE = 'IssueComponent') AS ec ON ec.ID = e_ji.ID
		LEFT JOIN us ON us.DESTINATION = e_ji.ID
	WHERE e_it.pname = 'Epic'),
ba_tasks AS (
	SELECT t_ji.ID, CONCAT_WS('-', t_prj.pkey, t_ji.issuenum) AS 'Key', t_ji.ASSIGNEE AS 'Assignee', t_ji.TIMESPENT AS 'Spent', ba_epics.Sprint AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS t_it ON t_it.ID = t_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS t_prj ON t_prj.ID = t_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS t_il ON t_il.DESTINATION = t_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
		INNER JOIN (SELECT * FROM epics WHERE epics.Component = 'Business Analysis') AS ba_epics ON ba_epics.ID = t_il.SOURCE
	WHERE t_it.pname != 'Bug' AND t_ilt.LINKNAME = 'Epic-Story Link'),
assignee_tasks AS (
	SELECT t_ji.ID, CONCAT_WS('-', t_prj.pkey, t_ji.issuenum) AS 'Key', t_ji.ASSIGNEE AS 'Assignee', t_ji.TIMESPENT AS 'Spent', box_epics.Sprint AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS t_it ON t_it.ID = t_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS t_prj ON t_prj.ID = t_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS t_il ON t_il.DESTINATION = t_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
		INNER JOIN (SELECT * FROM epics WHERE epics.Project = 'BSSBOX') AS box_epics ON box_epics.ID = t_il.SOURCE
	WHERE t_it.pname != 'Bug' AND t_ilt.LINKNAME = 'Epic-Story Link' AND t_ji.ASSIGNEE IN ('Anatoly.Akimov', 'Maksim.Grushka', 'YKudryavtseva', 'Mariia.Levanova', 'Elizaveta.Silina', 'Artem.Lavrentev', 'Roman.Bulin', 'Sergey.Talyanskiy', 'Anton.Kalashnikov', 'Pavel.Malygin')),
ba_subtasks AS (
	SELECT st_ji.ID, CONCAT_WS('-', st_prj.pkey, st_ji.issuenum) AS 'Key', st_ji.ASSIGNEE AS 'Assignee', st_ji.TIMESPENT AS 'Spent', ba_tasks.Sprint AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS st_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS st_it ON st_it.ID = st_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS st_prj ON st_prj.ID = st_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS st_il ON st_il.DESTINATION = st_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS st_ilt ON st_ilt.ID = st_il.LINKTYPE
		INNER JOIN ba_tasks ON ba_tasks.ID = st_il.SOURCE
	WHERE st_it.pname != 'Sub-bug' AND st_ilt.LINKNAME = 'jira_subtask_link'),
assignee_subtasks AS (
	SELECT st_ji.ID, CONCAT_WS('-', st_prj.pkey, st_ji.issuenum) AS 'Key', st_ji.ASSIGNEE AS 'Assignee', st_ji.TIMESPENT AS 'Spent', tasks.Sprint AS 'Sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS st_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS st_it ON st_it.ID = st_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS st_prj ON st_prj.ID = st_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS st_il ON st_il.DESTINATION = st_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS st_ilt ON st_ilt.ID = st_il.LINKTYPE
		INNER JOIN (
			SELECT t_ji.ID, box_epics.Sprint AS 'Sprint'
			FROM [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS t_il ON t_il.DESTINATION = t_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
				INNER JOIN (SELECT * FROM epics WHERE epics.Project = 'BSSBOX') AS box_epics ON box_epics.ID = t_il.SOURCE
			WHERE t_ilt.LINKNAME = 'Epic-Story Link') AS tasks on tasks.ID = st_il.SOURCE
	WHERE st_it.pname != 'Sub-bug' AND st_ilt.LINKNAME = 'jira_subtask_link' AND st_ji.ASSIGNEE IN ('Anatoly.Akimov', 'Maksim.Grushka', 'YKudryavtseva', 'Mariia.Levanova', 'Elizaveta.Silina', 'Artem.Lavrentev', 'Roman.Bulin', 'Sergey.Talyanskiy', 'Anton.Kalashnikov', 'Pavel.Malygin'))

SELECT BA.Sprint, (CASE WHEN BA.Spent IS NULL THEN '0' ELSE BA.Spent END) AS 'Spent'
FROM (
	SELECT * FROM ba_tasks
	UNION
	SELECT * FROM ba_subtasks
	UNION
	SELECT * FROM assignee_tasks
	UNION
	SELECT * FROM assignee_subtasks
) AS BA
ORDER BY BA.Sprint