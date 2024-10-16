from aws_cdk import Stack, CfnOutput, aws_bedrock as bedrock
from constructs import Construct


class GuardrailsStack(Stack):

    def __init__(self, 
        scope: Construct, 
        id: str,
        description: str,    
        config: dict,
        **kwargs):
        super().__init__(scope, id,description=description, **kwargs)

        global_guardrail = bedrock.CfnGuardrail(
            self,
            "global-guardrail",
            blocked_input_messaging="Blocked by guardrail",
            blocked_outputs_messaging="Blocked by guardrail",
            name="global-guardrail",
            # the properties below are optional
            contextual_grounding_policy_config=bedrock.CfnGuardrail.ContextualGroundingPolicyConfigProperty(
                filters_config=[
                    bedrock.CfnGuardrail.ContextualGroundingFilterConfigProperty(
                        threshold=0.5, type="GROUNDING"
                    )
                ]
            ),
        )

        global_guardrail_version = bedrock.CfnGuardrailVersion(
            self,
            "global-guardrail-version",
            guardrail_identifier=global_guardrail.attr_guardrail_id,
        )

        CfnOutput(self, "GuardrailName", value=global_guardrail.name)
        CfnOutput(
            self, "Guardrail Version", value=global_guardrail_version.attr_version
        )
