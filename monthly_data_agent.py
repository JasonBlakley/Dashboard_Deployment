#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Data Automation Agent
Automates the monthly data loading process for the Ticketing Dashboard
"""

import pandas as pd
import boto3
from botocore.client import Config
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class MonthlyDataAgent:
    """Automated agent for monthly dashboard data loading"""
    
    def __init__(self, config_path='automation_config.json'):
        """Initialize the agent with configuration"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.cos_client = self._init_cos_client()
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "cos": {
                    "bucket": "oidash-app",
                    "incoming_folder": "incoming",
                    "archive_folder": "archive"
                },
                "email": {
                    "recipients": [],
                    "sender": "dashboard-automation@ibm.com",
                    "subject_template": "Dashboard Data Updated - {month} {year}"
                },
                "files": {
                    "epm_pattern": "{month}_EPM_Tickets.csv",
                    "solve_pattern": "{month}_{year}_Solve.csv",
                    "output_pattern": "{month}_{year}_merged.csv"
                },
                "deployment": {
                    "auto_deploy": False,
                    "code_engine_app": "python-appid-app",
                    "code_engine_project": "python-appid-proj"
                }
            }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*80)
        self.logger.info("MONTHLY DATA AUTOMATION AGENT STARTED")
        self.logger.info("="*80)
    
    def _init_cos_client(self):
        """Initialize IBM Cloud Object Storage client"""
        cos_api_key = os.environ.get('IBM_CLOUD_APIKEY') or os.environ.get('APPID_COS_API_KEY')
        if not cos_api_key:
            self.logger.warning("COS API key not found in environment variables")
            return None
            
        service_instance_id = os.environ.get('COS_SERVICE_INSTANCE_ID', 
            'crn:v1:bluemix:public:cloud-object-storage:global:a/d9e0aa2e0e0e4b0e9e0e0e0e0e0e0e0e::')
        
        return boto3.client('s3',
            ibm_api_key_id=cos_api_key,
            ibm_service_instance_id=service_instance_id,
            ibm_auth_endpoint='https://iam.cloud.ibm.com/identity/token',
            config=Config(signature_version='oauth'),
            endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )
    
    def get_previous_month_info(self):
        """Get previous month's name and year"""
        today = datetime.now()
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        
        month_name = last_month.strftime('%B')  # Full month name
        month_abbr = last_month.strftime('%b')  # Abbreviated month name
        year = last_month.strftime('%Y')
        year_short = last_month.strftime('%y')
        
        return {
            'month_full': month_name,
            'month_abbr': month_abbr,
            'year': year,
            'year_short': year_short,
            'month_num': last_month.month,
            'date': last_month
        }
    
    def find_input_files(self, base_path='Files'):
        """Find EPM and Solve files for the previous month"""
        month_info = self.get_previous_month_info()
        
        # Build expected file paths
        year_path = Path(base_path) / month_info['year'] / month_info['month_abbr']
        
        # Try different naming patterns
        epm_patterns = [
            f"{month_info['month_abbr']}_EPM_Tickets.csv",
            f"{month_info['month_abbr']}_EPM_tickets.csv",
            f"{month_info['month_full']}_EPM_Tickets.csv"
        ]
        
        solve_patterns = [
            f"{month_info['month_full']}_{month_info['year_short']}_Solve.csv",
            f"{month_info['month_abbr']}_{month_info['year_short']}_Solve.csv",
            f"{month_info['month_full']}_{month_info['year']}_Solve.csv"
        ]
        
        epm_file = None
        solve_file = None
        
        # Search for EPM file
        for pattern in epm_patterns:
            potential_file = year_path / pattern
            if potential_file.exists():
                epm_file = potential_file
                break
        
        # Search for Solve file
        for pattern in solve_patterns:
            potential_file = year_path / pattern
            if potential_file.exists():
                solve_file = potential_file
                break
        
        return epm_file, solve_file, month_info
    
    def validate_solve_concept_quality(self, solve_data, month_info):
        """Validate concept coverage in Solve data before merge"""
        self.logger.info("Validating Solve concept quality...")
        
        concept_non_null = int(solve_data['Concept'].notna().sum())
        concept_pct = round((concept_non_null / len(solve_data)) * 100, 2) if len(solve_data) else 0.0
        
        concept_rank_zero_rows = 0
        if 'Concept Rank' in solve_data.columns:
            for value in solve_data['Concept Rank']:
                try:
                    if float(value) == 0.0:
                        concept_rank_zero_rows += 1
                except (TypeError, ValueError):
                    continue
        
        self.logger.info(f"  Concept non-null rows: {concept_non_null:,} / {len(solve_data):,} ({concept_pct}%)")
        self.logger.info(f"  Concept Rank = 0 rows: {concept_rank_zero_rows:,}")
        
        quality_config = self.config.get('quality_checks', {})
        min_concept_pct = quality_config.get('min_concept_pct', 40.0)
        fail_on_low_concept_pct = quality_config.get('fail_on_low_concept_pct', True)
        fail_on_concept_rank_zero = quality_config.get('fail_on_concept_rank_zero', True)
        
        issues = []
        if concept_pct < min_concept_pct:
            issues.append(
                f"Concept coverage {concept_pct}% is below minimum threshold of {min_concept_pct}%"
            )
        if concept_rank_zero_rows > 0:
            issues.append(
                f"Solve export contains {concept_rank_zero_rows:,} rows with Concept Rank = 0"
            )
        
        if issues:
            self.logger.error("Solve concept quality validation failed:")
            for issue in issues:
                self.logger.error(f"  - {issue}")
            self.logger.error(
                "  Likely cause: Solve export included Concept Rank 0 rows or used incorrect Cognos filters."
            )
            
            should_fail = (
                (fail_on_low_concept_pct and concept_pct < min_concept_pct) or
                (fail_on_concept_rank_zero and concept_rank_zero_rows > 0)
            )
            if should_fail:
                raise ValueError(
                    f"Solve concept quality check failed for {month_info['month_full']} {month_info['year']}. "
                    f"Review Solve export filters before continuing."
                )
        
        self.logger.info("  ✓ Solve concept quality validation passed")
    
    def merge_data(self, epm_file, solve_file, month_info):
        """Merge EPM and Solve data files"""
        self.logger.info(f"Merging data for {month_info['month_full']} {month_info['year']}")
        self.logger.info(f"  EPM file: {epm_file}")
        self.logger.info(f"  Solve file: {solve_file}")
        
        try:
            # Load EPM tickets data
            self.logger.info("Loading EPM tickets data...")
            epm_tickets = pd.read_csv(epm_file, encoding='UTF-16', sep='\t', on_bad_lines='skip')
            self.logger.info(f"  ✓ Loaded {len(epm_tickets):,} EPM records")
            
            # Load Solve data
            self.logger.info("Loading Solve data...")
            solve_data = pd.read_csv(solve_file, encoding='UTF-16', sep='\t', on_bad_lines='skip')
            self.logger.info(f"  ✓ Loaded {len(solve_data):,} Solve records")
            
            self.validate_solve_concept_quality(solve_data, month_info)
            
            # Select relevant columns from Solve data
            self.logger.info("Selecting relevant Solve columns...")
            solve_subset = solve_data[['Case Number', 'Open Month', 'Product',
                                       'Global Buying Group Name', 'Skill Case',
                                       'Concept', 'Concept Rank']]
            
            # Merge on Case Number
            self.logger.info("Merging datasets on 'Case Number'...")
            merged_df = epm_tickets.merge(solve_subset, on='Case Number', how='left')
            self.logger.info(f"  ✓ Merged dataset has {len(merged_df):,} records")
            
            # Apply standard transformations
            merged_df.rename(columns={
                'Global Buying Group Name_x': 'Global Buying Group Name',
                'Product_x': 'Product'
            }, inplace=True)
            
            merged_df['Date'] = pd.to_datetime(merged_df['Month'])
            
            # Drop Unnamed: 0 column if it exists
            if 'Unnamed: 0' in merged_df.columns:
                merged_df.drop(columns=['Unnamed: 0'], inplace=True)
            
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Error merging data: {e}")
            raise
    
    def save_merged_file(self, merged_df, month_info):
        """Save merged data to CSV file"""
        output_filename = f"{month_info['month_full']}_{month_info['year']}_merged.csv"
        output_path = Path('Files') / month_info['year'] / month_info['month_abbr'] / output_filename
        
        self.logger.info(f"Saving merged data to: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(output_path, index=False)
        
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        self.logger.info(f"  ✓ File saved successfully ({file_size_mb:.1f} MB)")
        
        return output_path
    
    def upload_to_cos(self, file_path, month_info):
        """Upload merged file to IBM Cloud Object Storage"""
        if not self.cos_client:
            self.logger.warning("COS client not initialized, skipping upload")
            return False
        
        bucket = self.config['cos']['bucket']
        object_name = file_path.name
        
        self.logger.info(f"Uploading to COS bucket '{bucket}'...")
        
        try:
            with open(file_path, 'rb') as file:
                self.cos_client.upload_fileobj(file, bucket, object_name)
            
            self.logger.info(f"  ✓ Uploaded to COS: {object_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading to COS: {e}")
            return False
    
    def trigger_deployment(self):
        """Trigger Code Engine deployment (optional)"""
        if not self.config['deployment']['auto_deploy']:
            self.logger.info("Auto-deployment disabled, skipping")
            return True
        
        self.logger.info("Triggering Code Engine deployment...")
        
        try:
            import subprocess
            
            app_name = self.config['deployment']['code_engine_app']
            project_name = self.config['deployment']['code_engine_project']
            
            # Select the Code Engine project
            subprocess.run([
                'ibmcloud', 'ce', 'project', 'select', 
                '--name', project_name
            ], check=True, capture_output=True)
            
            # Trigger application update
            result = subprocess.run([
                'ibmcloud', 'ce', 'application', 'update',
                '--name', app_name,
                '--build-source', 'https://github.com/JasonBlakley/Dashboard_Deployment.git',
                '--build-commit', 'main'
            ], check=True, capture_output=True, text=True)
            
            self.logger.info("  ✓ Deployment triggered successfully")
            self.logger.info(f"  Output: {result.stdout}")
            return True
            
        except Exception as e:
            if e.__class__.__name__ == 'CalledProcessError':
                self.logger.error(f"Error triggering deployment: {e}")
                self.logger.error(f"  Output: {getattr(e, 'output', '')}")
                return False
            self.logger.error(f"Error triggering deployment: {e}")
            return False
    
    def send_notification(self, success, month_info, details):
        """Send email notification about the automation result"""
        if not self.config['email']['recipients']:
            self.logger.info("No email recipients configured, skipping notification")
            return
        
        subject = self.config['email']['subject_template'].format(
            month=month_info['month_full'],
            year=month_info['year']
        )
        
        if success:
            body = f"""
Dashboard Data Automation - SUCCESS

Month: {month_info['month_full']} {month_info['year']}
Status: ✓ Completed Successfully

Details:
{details}

The dashboard has been updated with the latest data.

---
Automated by Monthly Data Agent
            """
        else:
            body = f"""
Dashboard Data Automation - FAILED

Month: {month_info['month_full']} {month_info['year']}
Status: ✗ Failed

Error Details:
{details}

Please check the logs and run the automation manually.

---
Automated by Monthly Data Agent
            """
        
        self.logger.info(f"Sending notification email to {len(self.config['email']['recipients'])} recipient(s)")
        self.logger.info(f"Subject: {subject}")
        self.logger.info(f"Body:\n{body}")
        
        # Note: Actual email sending would require SMTP configuration
        # This is a placeholder for the email functionality
    
    def run(self, epm_file=None, solve_file=None):
        """Run the complete automation workflow"""
        try:
            # Find input files if not provided
            if not epm_file or not solve_file:
                self.logger.info("Searching for input files...")
                epm_file, solve_file, month_info = self.find_input_files()
                
                if not epm_file or not solve_file:
                    error_msg = f"Could not find required files for {month_info['month_full']} {month_info['year']}"
                    self.logger.error(error_msg)
                    self.send_notification(False, month_info, error_msg)
                    return False
            else:
                month_info = self.get_previous_month_info()
            
            # Merge data
            merged_df = self.merge_data(epm_file, solve_file, month_info)
            
            # Save merged file
            output_path = self.save_merged_file(merged_df, month_info)
            
            # Upload to COS
            upload_success = self.upload_to_cos(output_path, month_info)
            
            # Trigger deployment (optional)
            deploy_success = self.trigger_deployment()
            
            # Prepare success details
            details = f"""
Records merged: {len(merged_df):,}
Output file: {output_path}
COS upload: {'✓ Success' if upload_success else '✗ Failed'}
Deployment: {'✓ Triggered' if deploy_success else '⊘ Skipped' if not self.config['deployment']['auto_deploy'] else '✗ Failed'}
            """
            
            self.logger.info("="*80)
            self.logger.info("AUTOMATION COMPLETED SUCCESSFULLY")
            self.logger.info("="*80)
            
            # Send success notification
            self.send_notification(True, month_info, details)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Automation failed: {e}", exc_info=True)
            
            month_info = self.get_previous_month_info()
            self.send_notification(False, month_info, str(e))
            
            return False


def main():
    """Main entry point for the automation agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monthly Data Automation Agent')
    parser.add_argument('--epm-file', help='Path to EPM tickets CSV file')
    parser.add_argument('--solve-file', help='Path to Solve data CSV file')
    parser.add_argument('--config', default='automation_config.json', 
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Create and run the agent
    agent = MonthlyDataAgent(config_path=args.config)
    success = agent.run(epm_file=args.epm_file, solve_file=args.solve_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Made with Bob