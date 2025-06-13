#!/usr/bin/env python3
"""
Jira API Script to fetch child issues of ISDOP-1
Author: [Pietro]
Date: [6 June 2025]
"""

from jira import JIRA
import sys

def connect_to_jira():
    """
    Establish connection to Jira using Personal Access Token
    """
    host = "https://jira.server.com/" # Replace with your URL
    pat = 'THE TOKEN'  # Replace with your actual Personal Access Token
    
    # Set up headers with Bearer token authentication
    headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
    headers["Authorization"] = f"Bearer {pat}"
    
    try:
        # Create Jira connection
        jira = JIRA(server=host, options={"headers": headers})
        print("✅ Successfully connected to Jira")
        return jira
    except Exception as e:
        print(f"❌ Failed to connect to Jira: {e}")
        sys.exit(1)

def run_jql_query(jira, jql_query):
    """
    Execute JQL query and return results
    """
    try:
        print(f"🔍 Executing query: {jql_query}")
        
        # Execute the JQL query
        # maxResults=50 limits results, increase if needed
        issues = jira.search_issues(jql_query, maxResults=50)
        
        print(f"📊 Found {len(issues)} issues")
        return issues
        
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return []

def display_results(issues):
    """
    Display the query results in a readable format
    """
    if not issues:
        print("📭 No issues found")
        return
    
    print("\n" + "="*80)
    print("QUERY RESULTS")
    print("="*80)
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. Issue Key: {issue.key}")
        print(f"   Summary: {issue.fields.summary}")
        print(f"   Status: {issue.fields.status.name}")
        print(f"   Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}")
        print(f"   Priority: {issue.fields.priority.name if issue.fields.priority else 'No Priority'}")
        print(f"   Issue Type: {issue.fields.issuetype.name}")
        print(f"   URL: {issue.permalink()}")
        print("-" * 40)

def main():
    """
    Main function to execute the script
    """
    print("🚀 Starting Jira Query Script")
    print("="*50)
    
    # Connect to Jira
    jira = connect_to_jira()
    
    # Define your JQL query
    jql_query = 'project = MYPROJECT AND issuekey in childIssuesOf("MYInititative-1ID")'
    
    # Execute the query
    issues = run_jql_query(jira, jql_query)
    
    # Display results
    display_results(issues)
    
    print(f"\n✅ Script completed successfully!")

if __name__ == "__main__":
    main()
