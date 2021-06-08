#!/usr/bin/env python3

# pylint: disable=invalid-name,ungrouped-imports

from aws_cdk import core as cdk
from cdk.cis_benchmark_service.cis_benchmark_stack import CISBenchmarkStack
from cdk.cis_benchmark_service.constants import BASE_NAME

app = cdk.App()
CISBenchmarkStack(app, BASE_NAME)

app.synth()
