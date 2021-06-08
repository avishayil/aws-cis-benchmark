import setuptools


with open("../README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="jupyter_ecs_service",
    version="0.0.1",

    description="AWS CDK stack for CIS Benchmark metrics and alerts",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Avishay Bar",

    package_dir={"": "cis_benchmark_service"},
    packages=setuptools.find_packages(where="cis_benchmark_service"),

    install_requires=[
        "aws-cdk.core>=1.107.0",
        "aws-cdk.aws-sns>=1.107.0",
        "aws-cdk.aws-iam>=1.107.0",
        "aws-cdk.aws-s3>=1.107.0",
        "aws-cdk.aws-sqs>=1.107.0",
        "aws-cdk.aws-cloudtrail>=1.107.0",
        "aws-cdk.aws-cloudwatch>=1.107.0",
        "aws-cdk.aws-cloudwatch-actions>=1.107.0",
        "PyYAML>=5.3.1",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
