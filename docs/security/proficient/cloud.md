---
title: Cloud Engineering
description: boto3 (AWS), Azure SDK, GCP, serverless and cloud-native Python
---

# Cloud Engineering <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="devops/">Python for DevOps</a></span>
  </div>
</div>

---

## AWS with boto3

```python
import boto3

# ─── S3 (object storage) ─────────────────────────
s3 = boto3.client("s3")

# Upload
s3.upload_file("local.txt", "my-bucket", "path/remote.txt")

# Download
s3.download_file("my-bucket", "path/remote.txt", "downloaded.txt")

# List objects
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="data/"):
    for obj in page.get("Contents", []):
        print(f"  {obj['Key']} ({obj['Size']} bytes)")

# Generate presigned URL (temporary access)
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": "secret.pdf"},
    ExpiresIn=3600,  # 1 hour
)

# ─── DynamoDB ─────────────────────────────────────
dynamo = boto3.resource("dynamodb")
table = dynamo.Table("users")

# Put item
table.put_item(Item={"user_id": "123", "name": "Alice", "age": 30})

# Get item
response = table.get_item(Key={"user_id": "123"})
print(response["Item"])

# Query
from boto3.dynamodb.conditions import Key
response = table.query(KeyConditionExpression=Key("user_id").eq("123"))

# ─── Lambda ───────────────────────────────────────
lambda_client = boto3.client("lambda")

# Invoke function
response = lambda_client.invoke(
    FunctionName="my-function",
    Payload=b'{"key": "value"}',
)
result = response["Payload"].read().decode()

# ─── SQS (message queue) ─────────────────────────
sqs = boto3.client("sqs")
queue_url = "https://sqs.us-east-1.amazonaws.com/123456/my-queue"

# Send message
sqs.send_message(QueueUrl=queue_url, MessageBody='{"task": "process_image", "id": 42}')

# Receive messages
response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20)
for msg in response.get("Messages", []):
    print(f"  Got: {msg['Body']}")
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
```

---

## AWS Lambda handler pattern

```python
import json
import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    """Process S3 upload events."""
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        # Download file
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")

        # Process
        processed = content.upper()

        # Upload result
        s3.put_object(
            Bucket=bucket,
            Key=f"processed/{key}",
            Body=processed.encode(),
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"processed": len(event["Records"])}),
    }
```

---

## Infrastructure with Pulumi (Python IaC)

```python
import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc", cidr_block="10.0.0.0/16")

# Create subnet
subnet = aws.ec2.Subnet("my-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
)

# Create an EC2 instance
instance = aws.ec2.Instance("web-server",
    instance_type="t3.micro",
    ami="ami-0c55b159cbfafe1f0",
    subnet_id=subnet.id,
    tags={"Name": "web-server"},
)

# Export outputs
pulumi.export("instance_ip", instance.public_ip)
pulumi.export("vpc_id", vpc.id)
```

---

## Practice Exercises

1. **Build an S3 file manager** — upload, download, list and delete with proper error handling.
2. **Create a Lambda function** that processes SQS messages and stores results in DynamoDB.
3. **Write a Pulumi stack** that creates a VPC, subnet, security group and EC2 instance.
4. **Implement a serverless API** with API Gateway + Lambda + DynamoDB.
5. **Build a cost monitor** that checks AWS billing daily and alerts if over budget.
6. **Write a multi-cloud abstraction** that works with both AWS S3 and GCP Cloud Storage.
