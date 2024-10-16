from aws_cdk import Stack, CfnOutput, aws_bedrock as bedrock

from constructs import Construct


class PromptStack(Stack):

    def __init__(self, 
        scope: Construct, 
        id: str,
        description: str,    
        config: dict,
        **kwargs):
        super().__init__(scope, id,description=description, **kwargs)

        model = bedrock.FoundationModel.from_foundation_model_id(
            self,
            "Model",
            bedrock.FoundationModelIdentifier.ANTHROPIC_CLAUDE_INSTANT_V1,
        )

        extraction_prompt = bedrock.CfnPrompt(
            self,
            "extraction-prompt",
            name="extraction-prompt",
            # the properties below are optional
            default_variant="defaultVariant",
            variants=[
                bedrock.CfnPrompt.PromptVariantProperty(
                    name="defaultVariant",
                    template_type="TEXT",
                    # the properties below are optional
                    inference_configuration=bedrock.CfnPrompt.PromptInferenceConfigurationProperty(
                        text=bedrock.CfnPrompt.PromptModelInferenceConfigurationProperty(
                            max_tokens=123,
                            stop_sequences=["stopSequences"],
                            temperature=0,
                            top_k=10,
                            top_p=1,
                        )
                    ),
                    model_id=model.model_id,
                    template_configuration=bedrock.CfnPrompt.PromptTemplateConfigurationProperty(
                        text=bedrock.CfnPrompt.TextPromptTemplateConfigurationProperty(
                            text="Generate some JSON objects about movies",
                        )
                    ),
                )
            ],
        )

        cfn_prompt_version = bedrock.CfnPromptVersion(
            self,
            "extraction-prompt-version",
            prompt_arn=extraction_prompt.attr_arn,
        )

        CfnOutput(self, "Prompt Name", value=extraction_prompt.name)
