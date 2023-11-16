import boto3
import json
import logging

default_log_args = {
    "level":  logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}

logging.basicConfig(**default_log_args)
logger = logging.getLogger("RouterLambda")

tablename = os.environ.get('TABLE_NAME')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(tablename)

sqs = boto3.client('sqs')
ec2 = boto3.client('ec2')

# 4 types of event in total: 3 from EC2, 1 one health
def handler(event, context):

    # Health change event
    if event['resources'] and event['source'] == 'aws.health':
        instance_id = event['resources']
        logger.info("Health event received for " + instance_id)

    # EC2 type of event
    else:
        instance_id = event['detail']['instance-id']
        logger.info("EC2 event received: "+ event['detail-type'] + " for " + instance_id)

    filters = [{
            'Name': 'tag:aws:eks:cluster-name',
            'Values': [
                '*'
            ]
        }]

    response = ec2.describe_instances(
        InstanceIds=[instance_id], Filters=filters
    )

    if response['Reservations']:
        for tag in response['Reservations'][0]['Instances'][0]['Tags']:
            if tag['Key'] == 'aws:eks:cluster-name':
                ClusterName = tag['Value']
            break
        logger.info("Instance belongs to " + ClusterName)

        try:
            response = table.get_item(Key={"ClusterName": ClusterName})
        except ClientError as err:
            logger.error("Cluster " + ClusterName + " not found")
            return {
                'statusCode': 200,
                'body': json.dumps("Cluster " + ClusterName + " not found, ignore instance " + instance_id)
            }
        else:
            queue_url = response['QueueUrl']
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(event)
            )
            logger.info("Message distributed to queue: " + ClusterName)

            return {
                'statusCode': 200,
                'body': json.dumps("Message distributed to queue:" + ClusterName)
            }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(instance_id+ " is not related to any EKS cluster")
        }