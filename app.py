from aws_cdk import App
from cdk_app_stack import PactBrokerFargateStack

app = App()
PactBrokerFargateStack(app, "PactBrokerDeploymentStack")
app.synth()