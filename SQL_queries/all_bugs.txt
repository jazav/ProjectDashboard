SELECT CONCAT_WS('-', prj.pkey, ji.issuenum) AS 'key', prj.pkey AS 'project', cmp.component AS 'component',
	(CASE WHEN ist.pname IN ('Backlog', 'New', 'Open', 'Reopened') THEN 'open' WHEN ist.pname IN ('Closed', 'Resolved') THEN LOWER(ist.pname) ELSE 'in fix' END) AS 'status'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
	INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
	INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it ON it.ID = ji.issuetype
	INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS ist ON ist.ID = ji.issuestatus
	LEFT JOIN (
		SELECT c_ji.ID AS 'ID', c_cmp.cname AS 'component'
		FROM [srv-jira-prod-report].[dbo].[jiraissue] AS c_ji
			INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS c_na ON c_na.SOURCE_NODE_ID = c_ji.ID
			INNER JOIN [srv-jira-prod-report].[dbo].[component] AS c_cmp ON c_cmp.ID = c_na.SINK_NODE_ID
		WHERE c_na.ASSOCIATION_TYPE = 'IssueComponent') AS cmp ON cmp.ID = ji.ID
WHERE it.pname IN ('Bug', 'Sub-bug') AND prj.pkey IN ('CNC', 'PSCPSC', 'CRAB', 'SSO', 'PCCM', 'GUS', 'BSSSCP', 'BSSCRMP', 'BSSDAPI', 'BSSCCM', 'BSSCPM', 'BSSCAM', 'BSSGUS', 'BSSUFM', 'BSSBFAM', 'BSSARBA', 'BSSPRMP',
													  'BSSBOX', 'NWMOCS', 'NWMPCRF', 'NWMUDR', 'BSSPRM', 'NWMAAA', 'NWM', 'BSSINFRA', 'BSSCRM', 'BSSORDER', 'RNDDOC', 'UIKIT', 'BSSPAY', 'BSSLIS', 'BSSPSC')
ORDER BY CONCAT_WS('-', prj.pkey, ji.issuenum)