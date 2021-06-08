# pylint: disable=no-value-for-parameter

import re
import yaml

from aws_cdk import (core,
                     aws_logs as logs,
                     aws_cloudtrail as trail,
                     aws_cloudwatch as cloudwatch,
                     aws_cloudwatch_actions as cloudwatch_actions,
                     aws_iam as iam,
                     aws_s3 as s3,
                     aws_kms as kms,
                     aws_sns as sns)

from constants import BASE_NAME, CLOUDTRAIL_METRICS


class CISBenchmarkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get Notifications Email from Parameter

        notifications_email_parameter = core.CfnParameter(self, "notificationsEmail", type="String",
                                                          default="security-depratment@domain.com",
                                                          description="Email for getting notifications")

        # SNS Topic for CIS Benchmark CloudWatch Alarms

        alarms_topic = sns.Topic(self, f'{BASE_NAME}AlarmsTopic',
                                 topic_name=f'{BASE_NAME}AlarmsTopic')

        sns.Subscription(self, f'{BASE_NAME}TargetSubscription',
                         endpoint=notifications_email_parameter.value_as_string,
                         protocol=sns.SubscriptionProtocol.EMAIL,
                         topic=alarms_topic)

        alarms_topic.add_to_resource_policy(
            iam.PolicyStatement(principals=[iam.ServicePrincipal('cloudwatch.amazonaws.com')],
                                actions=["sns:Publish"],
                                resources=[alarms_topic.topic_arn],
                                conditions={"StringEquals": {"aws:SourceOwner": self.account}}))

        # IAM Roles for CloudWatch Logs

        iam_role_for_logs = iam.Role(self,
                                     f'{BASE_NAME}RoleForCWLogs',
                                     role_name=f'{BASE_NAME}RoleForCWLogs',
                                     assumed_by=iam.ServicePrincipal('cloudtrail.amazonaws.com'))

        iam_role_for_logs.add_to_policy(iam.PolicyStatement(
            actions=['logs:CreateLogStream',
                     'logs:PutLogEvents'],
            resources=['*']))

        log_group = logs.LogGroup(self,
                                  f'{BASE_NAME}LogGroup',
                                  log_group_name=f'{BASE_NAME}LogGroup',
                                  retention=logs.RetentionDays.THREE_MONTHS,
                                  removal_policy=core.RemovalPolicy.DESTROY)

        management_trail_key = kms.Key(self,
                                       f'{BASE_NAME}ManagementTrailKey',
                                       enable_key_rotation=True,
                                       removal_policy=core.RemovalPolicy.DESTROY)

        management_trail_key.add_to_resource_policy(
            statement=iam.PolicyStatement(
                principals=[iam.ServicePrincipal(service='cloudtrail.amazonaws.com')],
                actions=['kms:Decrypt', 'kms:GenerateDataKey'],
                resources=['*']
            )
        )

        management_trail = trail.Trail(self,
                                       f'{BASE_NAME}ManagementEventsTrail',
                                       trail_name=f'{BASE_NAME}ManagementEventsTrail',
                                       cloud_watch_log_group=log_group,
                                       cloud_watch_logs_retention=None,
                                       send_to_cloud_watch_logs=True,
                                       enable_file_validation=True,
                                       include_global_service_events=True,
                                       is_multi_region_trail=True,
                                       kms_key=None,
                                       management_events=trail.ReadWriteType.ALL,
                                       )

        management_trail.log_all_s3_data_events(include_management_events=True,
                                                read_write_type=trail.ReadWriteType.ALL)

        management_trail.log_all_lambda_data_events(include_management_events=True,
                                                    read_write_type=trail.ReadWriteType.ALL)

        # CloudWatch Metric Filters and Alarms

        metric_filters = yaml.load(open("cdk/cis_benchmark_service/metric_filters.yml"), Loader=yaml.FullLoader)

        for fil in metric_filters:
            metric_filter = logs.MetricFilter(self,
                                              f'{BASE_NAME + fil["id"]}',
                                              log_group=log_group,
                                              filter_pattern=logs.FilterPattern().literal(fil["filter_pattern"]),
                                              metric_name=fil["metric_name"],
                                              metric_namespace=CLOUDTRAIL_METRICS)

            log_metric = cloudwatch.Metric(metric_name=fil["metric_name"], namespace=CLOUDTRAIL_METRICS)

            fil_alarm = cloudwatch.Alarm(self,
                                         f'{BASE_NAME + fil["id"]}Alarm',
                                         alarm_name=f'{BASE_NAME + fil["id"]}Alarm',
                                         alarm_description=fil["description"],
                                         metric=log_metric,
                                         statistic="Sum",
                                         period=core.Duration.seconds(amount=60),
                                         evaluation_periods=1,
                                         threshold=1,
                                         treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                                         comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD)

            fil_alarm_action = cloudwatch_actions.SnsAction(topic=alarms_topic)

            fil_alarm.add_alarm_action(fil_alarm_action)
