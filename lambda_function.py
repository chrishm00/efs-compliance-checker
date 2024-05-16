import os
import json
import boto3
import time

# Initialize boto3 clients
ssm_client = boto3.client('ssm')
config_client = boto3.client('config')
s3_client = boto3.client('s3')

# Specify the S3 bucket name where results will be saved
BUCKET_NAME = os.environ['BUCKET_NAME']

def evaluate_change_notification_compliance(configuration_item):
    # If the resource is not an EC2 instance, return NOT_APPLICABLE
    if configuration_item['resourceType'] != 'AWS::EC2::Instance':
        return {
            'compliance_type': 'NOT_APPLICABLE',
            'annotation': 'The rule does not apply to resources of type ' + configuration_item['resourceType'] + '.'
        }

    # Skip if the instance is not in a "running" state
    if configuration_item['configuration']['state']['name'] != 'running':
        return {
            'compliance_type': 'NOT_APPLICABLE',
            'annotation': 'The instance is not in a running state.'
        }

    try:
        # Send command to the instance to get mount details
        response = ssm_client.send_command(
            InstanceIds=[configuration_item['resourceId']],
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': ['cat /proc/mounts | grep nfs4']
            }
        )
        command_id = response['Command']['CommandId']
       
        # Wait for the command to execute
        time.sleep(10)
       
        output = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=configuration_item['resourceId']
        )
        # Extract EFS mounts
        lines = output['StandardOutputContent'].splitlines()
        efs_mounts = [line for line in lines if "efs" in line]
        
        if not efs_mounts:
            return {
                'compliance_type': 'COMPLIANT',
                'annotation': 'This EC2 instance is marked compliant as it does not have any EFS mounted.'
            }

        compliant_mounts = []
        non_compliant_mounts = []
        for mount in efs_mounts:
            if 'noresvport' in mount:
                compliant_mounts.append(mount)
            else:
                non_compliant_mounts.append(mount)
       
        # Save results to S3
        s3_path = save_to_s3(configuration_item['resourceId'], compliant_mounts, non_compliant_mounts)
       
        if non_compliant_mounts:
            return {
                'compliance_type': 'NON_COMPLIANT',
                'annotation': f"Please check the results stored in your S3 bucket: {s3_path}"
            }
        else:
            return {
                'compliance_type': 'COMPLIANT',
                'annotation': 'All EFS mounts on the instance have the noresvport option.'
            }
    except Exception as e:
        return {
            'compliance_type': 'NON_COMPLIANT',
            'annotation': f'Error checking the instance {configuration_item["resourceId"]}: {str(e)}'
        }

def save_to_s3(instance_id, compliant_mounts, non_compliant_mounts):
    # Create a dictionary with compliant and non-compliant EFS mounts
    data = {
        "Compliant": compliant_mounts,
        "NonCompliant": non_compliant_mounts
    }
   
    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)
   
    # Create a unique file name
    file_name = f"{instance_id}-{int(time.time())}.json"
   
    # Upload the JSON data to S3
    s3_client.put_object(Body=json_data, Bucket=BUCKET_NAME, Key=file_name)
   
    return f"s3://{BUCKET_NAME}/{file_name}"

def lambda_handler(event, context):
    # Parse the invokingEvent
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event['configurationItem']

    # Evaluate the configuration item for compliance
    evaluation = evaluate_change_notification_compliance(configuration_item)

    # Send the evaluation results to AWS Config
    response = config_client.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': configuration_item['resourceType'],
                'ComplianceResourceId': configuration_item['resourceId'],
                'ComplianceType': evaluation['compliance_type'],
                'Annotation': evaluation['annotation'],
                'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
            },
        ],
        ResultToken=event['resultToken']
    )
    return response
