WITH user_stories AS (
	SELECT us_ji.ID AS 'ID', (CASE WHEN us_pp1.ID IS NOT NULL THEN 'Pilot 1.0' ELSE NULL END) AS 'Pilot 1.0',
	(CASE WHEN us_pp2.ID IS NOT NULL THEN 'Pilot 2.0' ELSE NULL END) AS 'Pilot 2.0', us_it.pname AS 'issue type', CONCAT_WS('-', us_prj.pkey, us_ji.issuenum) AS 'key'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS us_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS us_it ON us_it.ID = us_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[customfieldvalue] AS us_cfv ON us_cfv.ISSUE = us_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS us_prj ON us_prj.ID = us_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS us_is ON us_is.ID = us_ji.issuestatus
		LEFT JOIN (
			SELECT pp_ji.ID
			FROM [srv-jira-prod-report].[dbo].[label] AS pp_lbl
				INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS pp_ji ON pp_ji.ID = pp_lbl.ISSUE
			WHERE pp_lbl.LABEL = 'PilotPriority') AS us_pp1 ON us_pp1.ID = us_ji.ID
		LEFT JOIN (
			SELECT pp_ji.ID
			FROM [srv-jira-prod-report].[dbo].[label] AS pp_lbl
				INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS pp_ji ON pp_ji.ID = pp_lbl.ISSUE
			WHERE pp_lbl.LABEL = 'Pilot2.0') AS us_pp2 ON us_pp2.ID = us_ji.ID
	WHERE us_prj.pname = 'BSSBOX' AND us_it.pname = 'User Story (L3)' AND us_cfv.STRINGVALUE = '7327' AND us_is.pname != 'Canceled'),
epics AS (
	SELECT e_ji.ID AS 'ID', (CASE WHEN epics_cmp.component IS NULL THEN '' ELSE epics_cmp.component END) AS 'component', user_stories.[Pilot 1.0] AS 'Pilot 1.0', user_stories.[Pilot 2.0] AS 'Pilot 2.0'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS e_il ON e_il.DESTINATION = e_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS e_ilt ON e_ilt.ID = e_il.LINKTYPE
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS e_ist ON e_ist.ID = e_ji.issuestatus
		INNER JOIN user_stories ON user_stories.ID = e_il.SOURCE
		LEFT JOIN (
			SELECT ec_ji.ID AS 'ID', ec_cmp.cname AS 'component'
			FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ec_ji
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS ec_il ON ec_il.DESTINATION = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS ec_ilt ON ec_ilt.ID = ec_il.LINKTYPE
				INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS ec_na ON ec_na.SOURCE_NODE_ID = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[component] AS ec_cmp ON ec_cmp.ID = ec_na.SINK_NODE_ID
			WHERE ec_ilt.LINKNAME = 'nexign_hierarchy_link' AND ec_il.SOURCE IN (SELECT ID FROM user_stories)
			    AND ec_na.ASSOCIATION_TYPE = 'IssueComponent') AS epics_cmp ON epics_cmp.ID = e_ji.ID
	WHERE e_ilt.LINKNAME = 'nexign_hierarchy_link' AND e_il.SOURCE IN (SELECT ID FROM user_stories) AND e_ist.pname != 'Canceled'
	    AND (epics_cmp.component NOT IN ('Documentation', 'QC Design', 'QC Testing') OR epics_cmp.component IS NULL)),
tasks AS (
	SELECT t_ji.ID AS 'ID', epics.component AS 'component', epics.[Pilot 1.0] AS 'Pilot 1.0', epics.[Pilot 2.0] AS 'Pilot 2.0', t_it.pname AS 'issue type'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS t_it ON t_it.ID = t_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS t_il ON t_il.DESTINATION = t_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
		INNER JOIN epics ON epics.ID = t_il.SOURCE
	WHERE t_it.pname != 'Bug' AND t_ilt.LINKNAME = 'Epic-Story Link' AND t_il.SOURCE IN (SELECT ID FROM epics)),
subtasks AS (
	SELECT st_ji.ID AS 'ID', tasks.component AS 'component', tasks.[Pilot 1.0] AS 'Pilot 1.0', tasks.[Pilot 2.0] AS 'Pilot 2.0', st_it.pname AS 'issue type'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS st_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS st_it ON st_it.ID = st_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS st_il ON st_il.DESTINATION = st_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS st_ilt ON st_ilt.ID = st_il.LINKTYPE
		INNER JOIN tasks ON tasks.ID = st_il.SOURCE
	WHERE st_it.pname != 'Sub-bug' AND st_ilt.LINKNAME = 'jira_subtask_link' AND st_il.SOURCE IN (SELECT ID FROM tasks))

SELECT user_stories.[Pilot 1.0] AS 'Pilot 1.0', user_stories.[Pilot 2.0] AS 'Pilot 2.0', user_stories.[issue type] AS 'issue type', user_stories.[key] AS 'key',
	NULL AS 'component', NULL AS 'status', NULL AS 'resolutiondate', NULL AS 'created', NULL AS 'timeoriginalestimate', NULL AS 'timespent'
FROM user_stories
UNION
SELECT issues.[Pilot 1.0] AS 'Pilot 1.0', issues.[Pilot 2.0] AS 'Pilot 2.0', issues.[issue type] AS 'issue type', CONCAT_WS('-', prj.pkey, ji.issuenum) AS 'key', issues.component AS 'component', ist.pname AS 'status', CONVERT(date, ji.RESOLUTIONDATE) AS 'resolutiondate',
	CONVERT(date, ji.CREATED) AS 'created', (CASE WHEN ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, ji.TIMEORIGINALESTIMATE))/28800) AS numeric(17,3)) END) AS 'timeoriginalestimate',
	(CASE WHEN ji.TIMESPENT IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, ji.TIMESPENT))/28800) AS numeric(17,3)) END) AS 'timespent'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
	INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS ist ON ist.ID = ji.issuestatus
	INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
	INNER JOIN (SELECT * FROM tasks UNION SELECT * FROM subtasks) AS issues ON issues.ID = ji.ID
WHERE ist.pname != 'Canceled'
ORDER BY [resolutiondate]