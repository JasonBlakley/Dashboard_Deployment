#!/bin/bash
# Deploy Monthly Data Automation Agent to IBM Cloud Functions
# This script creates a serverless function that can be scheduled to run monthly

set -e

echo "================================================================================"
echo "                 DEPLOYING MONTHLY DATA AUTOMATION AGENT                       "
echo "                      TO IBM CLOUD FUNCTIONS                                   "
echo "================================================================================"
echo ""

# Configuration
FUNCTION_NAME="monthly-data-agent"
NAMESPACE="default"
TRIGGER_NAME="monthly-trigger"
RULE_NAME="monthly-rule"
MEMORY="512"
TIMEOUT="600000"  # 10 minutes in milliseconds

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo "❌ IBM Cloud CLI not found. Please install it first:"
    echo "   https://cloud.ibm.com/docs/cli"
    exit 1
fi

# Check if logged in
if ! ibmcloud target &> /dev/null; then
    echo "❌ Not logged in to IBM Cloud. Please run:"
    echo "   ibmcloud login"
    exit 1
fi

echo "✓ IBM Cloud CLI found and logged in"
echo ""

# Check if Cloud Functions plugin is installed
if ! ibmcloud fn namespace list &> /dev/null; then
    echo "Installing Cloud Functions plugin..."
    ibmcloud plugin install cloud-functions
fi

echo "✓ Cloud Functions plugin ready"
echo ""

# Select namespace
echo "Available namespaces:"
ibmcloud fn namespace list
echo ""
read -p "Enter namespace to use (or press Enter for 'default'): " input_namespace
NAMESPACE=${input_namespace:-$NAMESPACE}

echo "Using namespace: $NAMESPACE"
ibmcloud fn property set --namespace $NAMESPACE
echo ""

# Create deployment package
echo "[1/5] Creating deployment package..."
TEMP_DIR=$(mktemp -d)
cp monthly_data_agent.py "$TEMP_DIR/__main__.py"
cp automation_config.json "$TEMP_DIR/"

# Create requirements.txt for the function
cat > "$TEMP_DIR/requirements.txt" << EOF
pandas==2.0.3
ibm-cos-sdk==2.13.0
EOF

# Create Cloud Functions handler wrapper
cat > "$TEMP_DIR/cloud_function_handler.py" << 'EOF'
"""
IBM Cloud Functions Handler for Monthly Data Agent
"""
import sys
import os
from monthly_data_agent import MonthlyDataAgent

def main(params):
    """
    Cloud Functions entry point
    
    Parameters:
    - epm_file: Optional path to EPM file
    - solve_file: Optional path to Solve file
    - config: Optional config file path
    """
    try:
        # Get parameters
        epm_file = params.get('epm_file')
        solve_file = params.get('solve_file')
        config_file = params.get('config', 'automation_config.json')
        
        # Create and run agent
        agent = MonthlyDataAgent(config_path=config_file)
        success = agent.run(epm_file=epm_file, solve_file=solve_file)
        
        if success:
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Automation completed successfully',
                    'success': True
                }
            }
        else:
            return {
                'statusCode': 500,
                'body': {
                    'message': 'Automation failed',
                    'success': False
                }
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'message': f'Error: {str(e)}',
                'success': False
            }
        }
EOF

# Create zip package
cd "$TEMP_DIR"
zip -r function.zip . > /dev/null
cd - > /dev/null

echo "✓ Deployment package created"
echo ""

# Deploy the function
echo "[2/5] Deploying function to IBM Cloud..."
ibmcloud fn action update $FUNCTION_NAME \
    --kind python:3.9 \
    --memory $MEMORY \
    --timeout $TIMEOUT \
    "$TEMP_DIR/function.zip"

echo "✓ Function deployed: $FUNCTION_NAME"
echo ""

# Set environment variables (secrets)
echo "[3/5] Configuring environment variables..."
echo ""
echo "The function needs the following environment variables:"
echo "  - IBM_CLOUD_APIKEY (for COS access)"
echo ""

read -p "Do you want to set IBM_CLOUD_APIKEY now? (y/n): " set_apikey
if [[ $set_apikey == "y" || $set_apikey == "Y" ]]; then
    read -sp "Enter IBM Cloud API Key: " apikey
    echo ""
    
    ibmcloud fn action update $FUNCTION_NAME \
        --param IBM_CLOUD_APIKEY "$apikey"
    
    echo "✓ API key configured"
else
    echo "⚠ Skipping API key configuration"
    echo "  You can set it later with:"
    echo "  ibmcloud fn action update $FUNCTION_NAME --param IBM_CLOUD_APIKEY <key>"
fi
echo ""

# Create trigger (schedule)
echo "[4/5] Creating monthly trigger..."
echo ""
echo "Schedule options:"
echo "  1. 2nd of month at 3:00 AM (recommended)"
echo "  2. 1st of month at 9:00 AM"
echo "  3. Custom cron expression"
echo ""
read -p "Select option (1-3): " schedule_option

case $schedule_option in
    1)
        CRON="0 3 2 * *"
        ;;
    2)
        CRON="0 9 1 * *"
        ;;
    3)
        read -p "Enter cron expression (e.g., '0 3 2 * *'): " CRON
        ;;
    *)
        echo "Invalid option, using default: 2nd of month at 3:00 AM"
        CRON="0 3 2 * *"
        ;;
esac

# Delete existing trigger if it exists
ibmcloud fn trigger delete $TRIGGER_NAME 2>/dev/null || true

# Create new trigger
ibmcloud fn trigger create $TRIGGER_NAME \
    --feed /whisk.system/alarms/alarm \
    --param cron "$CRON" \
    --param trigger_payload '{"auto_detect": true}'

echo "✓ Trigger created: $TRIGGER_NAME (cron: $CRON)"
echo ""

# Create rule to connect trigger to action
echo "[5/5] Creating rule to connect trigger and action..."

# Delete existing rule if it exists
ibmcloud fn rule delete $RULE_NAME 2>/dev/null || true

# Create new rule
ibmcloud fn rule create $RULE_NAME $TRIGGER_NAME $FUNCTION_NAME

echo "✓ Rule created: $RULE_NAME"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

# Test the function
echo "================================================================================"
echo "                           DEPLOYMENT COMPLETE                                  "
echo "================================================================================"
echo ""
echo "Function Details:"
echo "  Name: $FUNCTION_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Memory: ${MEMORY}MB"
echo "  Timeout: $((TIMEOUT/1000)) seconds"
echo "  Schedule: $CRON"
echo ""
echo "Next Steps:"
echo "  1. Test the function:"
echo "     ibmcloud fn action invoke $FUNCTION_NAME --result"
echo ""
echo "  2. View function logs:"
echo "     ibmcloud fn activation poll"
echo ""
echo "  3. List all activations:"
echo "     ibmcloud fn activation list"
echo ""
echo "  4. Update configuration:"
echo "     Edit automation_config.json and redeploy"
echo ""
echo "  5. Manual trigger:"
echo "     ibmcloud fn trigger fire $TRIGGER_NAME"
echo ""
echo "The function will automatically run on schedule: $CRON"
echo ""

read -p "Would you like to test the function now? (y/n): " test_now
if [[ $test_now == "y" || $test_now == "Y" ]]; then
    echo ""
    echo "Testing function..."
    ibmcloud fn action invoke $FUNCTION_NAME --result --blocking
fi

echo ""
echo "✓ Deployment complete!"
echo ""

# Made with Bob