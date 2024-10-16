from aws_cdk import Stage, DefaultStackSynthesizer
from constructs import Construct

from infrastructure.ecr_stack import EcrStack
from infrastructure.lambdas.example_lambda import ExampleLambda
from infrastructure.s3bucket_stack import S3Stack
from infrastructure.batch.job_defs_stack import JobDefsStack
from infrastructure.lambdas.infra import LambdaCognitoStack

from cdk_nag import AwsSolutionsChecks, NagSuppressions

from bedrockstack.automation_stack import AutomationStack
from bedrockstack.guardrails_stack import GuardrailsStack
from bedrockstack.prompt_stack import PromptStack

from aws_cdk import (
    Stage,
    # Import Aspects
    Aspects
)


class AppDeployBootstrap(Stage):
    def __init__(self, scope: Construct, id: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        ecr_repo = EcrStack(
            self,
            "EcrRepoStack",
            config=config,
            synthesizer=DefaultStackSynthesizer(),
        )


class AppDeploy(Stage):
    def __init__(self, scope: Construct, id: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        # s3 bucket Stack Example
        s3bucket = S3Stack(self, "S3Stack", config=config)

        # put stage id into configuration object for use in JobDefStack
        config["stage"] = id
        # Job Definition Example ...
        jobdefs = JobDefsStack(
            self,
            "Job-Defs",
            "JobDefinitions",
            config,
        )

        # lambda Stack example
        example_lambda = ExampleLambda(
            self,
            "LambdaStack",
            "LambdaDesciption",
            config=config,
        )
        """
        lambda_cognito = LambdaCognitoStack(
        self,
        "LambdaCogStack",
        "LambdaCogDesciption",
        config=config,
        )

        Aspects.of(lambda_cognito).add(AwsSolutionsChecks(verbose=True))
        # Add Suppression
        NagSuppressions.add_stack_suppressions(stack=lambda_cognito, suppressions=[
            {"id": "AwsSolutions-IAM4", "reason": "Policies are set by the Construct."}
        ])
        """

        automation_stack = AutomationStack(
        self,
        "AutomationStack",
        "Automation with StepFunctions",
        config=config,
        )

        guardrails_stack = GuardrailsStack(
        self,
        "GuardrailsStack",
        "Bedrock Guardrails",
        config=config,
        )

        prompt_stack = PromptStack(
        self,
        "PromptStack",
        "Bedrock Prompts",
        config=config,
        )

        


