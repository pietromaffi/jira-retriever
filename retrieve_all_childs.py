#!/usr/bin/env python3
"""
Jira API Script to fetch Business Initiatives and their child issues
Creates CSV files with batches of 10 Business Initiatives
Author: [Pietro]
Date: [10/06/2025]
"""

from jira import JIRA
import csv
import sys
from datetime import datetime
import os

def connect_to_jira():
    """
    Establish connection to Jira using Personal Access Token
    """
    host = "https://jira.server.com/"
    pat = 'MY TOKEN'  # Replace with your actual Personal Access Token
    
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

def get_business_initiatives(jira):
    """
    Get all Business Initiatives from ISDOP project
    """
    jql_query = 'project = MYPROJECT AND issuetype = "Business Initiative"'
    
    try:
        print(f"🔍 Fetching Business Initiatives...")
        print(f"Query: {jql_query}")
        
        # Get all Business Initiatives (increase maxResults if needed or manage it in case of limits)
        business_initiatives = jira.search_issues(jql_query, maxResults=1000)
        
        print(f"📊 Found {len(business_initiatives)} Business Initiatives")
        return business_initiatives
        
    except Exception as e:
        print(f"❌ Error fetching Business Initiatives: {e}")
        return []

def get_child_issues(jira, parent_key):
    """
    Get all child issues for a given parent issue
    """
    jql_query = f'project = ISDOP AND issuekey in childIssuesOf("{parent_key}")'
    
    try:
        child_issues = jira.search_issues(jql_query, maxResults=200)
        print(f"   └─ {parent_key}: {len(child_issues)} child issues")
        return child_issues
        
    except Exception as e:
        print(f"❌ Error fetching child issues for {parent_key}: {e}")
        return []

def format_date(date_string):
    """
    Format Jira date string to readable format
    """
    if not date_string:
        return "No date"
    
    try:
        # Parse Jira datetime format and convert to readable format
        dt = datetime.strptime(date_string[:19], "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_string

def create_csv_file(batch_data, batch_number):
    """
    Create CSV file for a batch of Business Initiatives and their children
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"isdop_batch_{batch_number}_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Business Initiative', 
                'BI Summary', 
                'Child Issue Key', 
                'Summary', 
                'Status', 
                'Issue Type', 
                'URL', 
                'Create Date'
            ])
            
            # Write data
            for row in batch_data:
                writer.writerow(row)
        
        print(f"📄 Created: {filename} ({len(batch_data)} records)")
        return filename
        
    except Exception as e:
        print(f"❌ Error creating CSV file {filename}: {e}")
        return None

def process_business_initiatives(jira, business_initiatives):
    """
    Process all Business Initiatives and create batched CSV files
    """
    batch_size = 10
    current_batch = []
    batch_number = 1
    total_child_issues = 0
    created_files = []
    
    print(f"\n🔄 Processing Business Initiatives in batches of {batch_size}...")
    print("="*80)
    
    for i, bi in enumerate(business_initiatives, 1):
        print(f"\n📋 Processing BI {i}/{len(business_initiatives)}: {bi.key}")
        print(f"   Summary: {bi.fields.summary}")
        
        # Get child issues for this Business Initiative
        child_issues = get_child_issues(jira, bi.key)
        total_child_issues += len(child_issues)
        
        # If no child issues, add a row indicating this
        if not child_issues:
            row = [
                bi.key,
                bi.fields.summary,
                "No child issues",
                "No child issues found",
                "-",
                "-",
                "-",
                "-"
            ]
            current_batch.append(row)
        else:
            # Add each child issue as a row
            for child in child_issues:
                row = [
                    bi.key,
                    bi.fields.summary,
                    child.key,
                    child.fields.summary,
                    child.fields.status.name,
                    child.fields.issuetype.name,
                    child.permalink(),
                    format_date(child.fields.created)
                ]
                current_batch.append(row)
        
        # Check if we need to create a CSV file (every 10 BIs or last BI)
        if i % batch_size == 0 or i == len(business_initiatives):
            filename = create_csv_file(current_batch, batch_number)
            if filename:
                created_files.append(filename)
            current_batch = []
            batch_number += 1
    
    return created_files, total_child_issues

def print_summary(business_initiatives, created_files, total_child_issues):
    """
    Print final summary of the process
    """
    print("\n" + "="*80)
    print("📊 PROCESSING SUMMARY")
    print("="*80)
    print(f"Business Initiatives processed: {len(business_initiatives)}")
    print(f"Total child issues found: {total_child_issues}")
    print(f"CSV files created: {len(created_files)}")
    print("\n📁 Created files:")
    for i, filename in enumerate(created_files, 1):
        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        print(f"   {i}. {filename} ({file_size:,} bytes)")

def main():
    """
    Main function to execute the script
    """
    print("🚀 Starting ISDOP Business Initiative Analysis")
    print("="*60)
    
    # Connect to Jira
    jira = connect_to_jira()
    
    # Get all Business Initiatives
    business_initiatives = get_business_initiatives(jira)
    
    if not business_initiatives:
        print("❌ No Business Initiatives found. Exiting.")
        return
    
    # Process Business Initiatives and create CSV files
    created_files, total_child_issues = process_business_initiatives(jira, business_initiatives)
    
    # Print summary
    print_summary(business_initiatives, created_files, total_child_issues)
    
    print(f"\n✅ Script completed successfully!")

if __name__ == "__main__":
    main()
