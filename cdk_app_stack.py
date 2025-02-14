from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_rds as rds,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs_patterns as ecs_patterns,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_ecr as ecr,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class PactBrokerFargateStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "PactBrokerVPC", max_azs=2)

        # Create Secret for Database Credentials
        db_secret = secretsmanager.Secret(self, "PactBrokerDBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template="{\"username\":\"pactbrokeruser\"}",
                generate_string_key="password",
                exclude_characters="\"@/ "
            )
        )

        # Create Aurora Serverless v2 Cluster
        db_cluster = rds.DatabaseCluster(self, "PactBrokerDB",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_13_18
            ),
            writer=rds.ClusterInstance.serverless_v2("WriterInstance"),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_secret),
            default_database_name="pactbroker"
        )

        # Create ECS Cluster
        ecs_cluster = ecs.Cluster(self, "PactBrokerCluster", vpc=vpc)

        # Create an ECR repository if it doesn't exist
        ecr_repo = ecr.Repository(self, "PactBrokerECR", repository_name="pact-broker")

        # Define Log Group
        log_group = logs.LogGroup(self, "PactBrokerLogGroup",
            retention=logs.RetentionDays.ONE_WEEK
        )

        # Create Fargate Task Definition
        task_definition = ecs.FargateTaskDefinition(self, "PactBrokerTask",
            memory_limit_mib=512,
            cpu=256
        )

        # Add execution role to allow pulling images from ECR
        task_definition.add_to_execution_role_policy(iam.PolicyStatement(
            actions=["ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "ecr:GetAuthorizationToken"],
            resources=["*"]
        ))

        container = task_definition.add_container("PactBrokerContainer",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repo, "latest"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="PactBroker", log_group=log_group),
            environment={
                "PACT_BROKER_DATABASE_USERNAME": "pactbrokeruser",
                "PACT_BROKER_DATABASE_HOST": db_cluster.cluster_endpoint.hostname,
                "PACT_BROKER_DATABASE_NAME": "pactbroker"
            },
            secrets={
                "PACT_BROKER_DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password")
            }
        )

        container.add_port_mappings(ecs.PortMapping(container_port=9292))

        # Create ALB Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "PactBrokerService",
            cluster=ecs_cluster,
            task_definition=task_definition,
            public_load_balancer=True
        )

        # Grant database access to ECS tasks
        db_cluster.connections.allow_default_port_from(fargate_service.service)

        # Output the ALB DNS
        CfnOutput(self, "PactBrokerURL", value=fargate_service.load_balancer.load_balancer_dns_name)
