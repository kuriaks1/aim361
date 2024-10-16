from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_bedrock as bedrock,
    aws_lambda as lambda_,
    aws_iam as iam,
)

from constructs import Construct
from aws_solutions_constructs.aws_s3_stepfunctions import S3ToStepfunctions


class AutomationStack(Stack):

    def __init__(self, 
        scope: Construct, 
        id: str,
        description: str,    
        config: dict,
        **kwargs):
        super().__init__(scope, id,description=description, **kwargs)

        # Create input and output S3 buckets
        input_bucket = s3.Bucket(
            self,
            "input-bucket",
            enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            event_bridge_enabled=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        output_bucket = s3.Bucket(
            self,
            "output-bucket",
            enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
        )

        model = bedrock.FoundationModel.from_foundation_model_id(
            self,
            "Model",
            bedrock.FoundationModelIdentifier.ANTHROPIC_CLAUDE_INSTANT_V1,
        )

        bedrock_lambda = lambda_.Function(
            self,
            "bedrock-lambda",
            handler="lambda_function.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("lambdas/bedrock"),
            environment={"GUARDRAIL": "RIV-test", "modelId": model.model_id},
            tracing=lambda_.Tracing.ACTIVE,
            timeout=Duration.minutes(10),
        )

        bedrock_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )

        bedrock_task1 = tasks.LambdaInvoke(
            self,
            "invoke-bedrock-lambda1",
            lambda_function=bedrock_lambda,
            payload=sfn.TaskInput.from_object({"body": sfn.JsonPath.entire_payload}),
            payload_response_only=True,
            result_path="$.Payload",
        )

        bedrock_task2 = tasks.LambdaInvoke(
            self,
            "invoke-bedrock-lambda2",
            lambda_function=bedrock_lambda,
            payload=sfn.TaskInput.from_object({"body": sfn.JsonPath.entire_payload}),
            payload_response_only=True,
            result_path="$.Payload",
        )

        s3_output_task = tasks.CallAwsService(
            self,
            "s3-output-task",
            service="s3",
            action="putObject",
            parameters={
                "Body": sfn.JsonPath.string_at("$"),
                "Bucket": output_bucket.bucket_name,
                "Key": sfn.JsonPath.string_at("$.detail.object.key"),
            },
            iam_resources=[output_bucket.arn_for_objects("*")],
        )

        # bedrockTask = tasks.BedrockInvokeModel(
        #     self,
        #     "Generate Book Summary",
        #     # Choose the model to invoke
        #     model=model,
        #     # Provide the input to the model, including the prompt and inference properties
        #     body=sfn.TaskInput.from_object(
        #         {
        #             "anthropic_version": "bedrock-2023-05-31",
        #             "messages": [
        #                 {
        #                     "role": "user",
        #                     "content": [
        #                         {
        #                             "type": "text",
        #                             # The prompt
        #                             "text": "Write a 1-2 sentence summary for the book Pride & Prejudice.",
        #                         }
        #                     ],
        #                 }
        #             ],
        #             "max_tokens": 250,
        #             "temperature": 1,
        #         }
        #     ),
        #     # Extract the response from the model
        #     output_path="$.Body.content[0].text",
        # )

        # Define the Step Function S3 event

        s3ToStepfunction = S3ToStepfunctions(
            self,
            "step-function",
            state_machine_props=sfn.StateMachineProps(
                definition=bedrock_task1.next(bedrock_task2).next(s3_output_task),
                tracing_enabled=True,
            ),
            existing_bucket_obj=input_bucket,
        )

        # Create the Step Function Tasks

        CfnOutput(self, "InputBucketName", value=input_bucket.bucket_name)
        CfnOutput(self, "OutputBucketName", value=output_bucket.bucket_name)
        CfnOutput(
            self,
            "StepFunctionName",
            value=s3ToStepfunction.state_machine.state_machine_name,
        )
