# Enhance spot instance interruption handling in multi-cluster environment using Karpenter and Lambda

The Lambda function works as a centralized event processor. All events are sent to the function instead of individual SQS queue. When an event is received, the function obtains tags from Amazon EC2 API by instance ID in the event. Therefore, the function determines which cluster the instance belongs to, and delivers the event to the corresponding queue accordingly.
