import os
import boto3
import json

bedrock = boto3.client(service_name="bedrock-runtime")


def lambda_handler(event, context):
    bucket = event["detail"]["bucket"]["name"]
    key = event["detail"]["object"]["key"]

    message_list = []

    initial_message = {
        "role": "user",
        "content": [{"text": "How are you today?"}],
    }

    message_list.append(initial_message)

    response = bedrock.converse(
        modelId=os.getenv("modelId"),
        messages=message_list,
        inferenceConfig={"maxTokens": 2000, "temperature": 0},
    )

    response_message = response["output"]["message"]

    return {
        "status": "SUCCEEDED",
        "s3Path": "/".join(
            [event["detail"]["bucket"]["name"], event["detail"]["object"]["key"]]
        ),
        "llm-response": response_message,
        "variable": os.getenv("GUARDRAIL"),
    }
