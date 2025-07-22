Project Overview -
This project delivers an automated end-to-end AWS solution built with AWS CDK as our infrastructure as code tool and deployed by a manual GitHub Actions workflow.

It creates an S# bucket and uploads sample files during every deploy.
It deploys a Python 3.9 Lambda function that:
lists every object in the bucket
publishes execution details to an SNS topic
returns {"objects": [...]} to the caller.
Publishes execution details to an SNS topic that has an e-mail subscription.
Uses a least-privilege IAM role granting only the S3 read and SNS publish actions the Lambda needs.

Repository layout -

infrastructure/ - the CDK app - defines all the AWS resources (S3 bucket, SNS Topic, IAM role, Lambda).

lambda/list_objects/ - defines a lambda handler inside index.py, which lists bucket objects and publishes execution details to an SNS topic.

sample_files/ - Two random images to test that they are indeed loaded into the bucket upon deployment.

tests/ - Manual trigger script and event.json file, responsible for invoking the lambda locally.
It is essentially a one click script that invokes the lambda via AWS CLI, it defines the lambda function name, and uses the "aws lambda invoke" to invoke it, and prints the json response.

.github/workflows/ - Defines a simple yml file called basic_workflow_dispatch.yml which is a GitHub actions workflow that bootstraps and deploys the stack.

Setup & Deployment
Fork / Clone the repo
In your github repo, add repo secrets (Settings -> Secrets -> Actions)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (e.g us-east-1)

Open actions -> Manual CDK Deploy -> Run workflow
The workflow will:
Check out the code
Configure AWS credentials
Install CDK CLI and Python dependencies
Run cdk bootstrap and cdk deploy --all
Watch the run logs, on success you will have a bucket, SNS topic and Lambda deployed.


* Manual Lambda test instructions
Ensure AWS CLI is configured (aws configure)
Run the script from the repository root:
# cmd
cd tests
invoke_lambda.bat

Or, if using powershell:
* Rename invoke_lambda.bat to invoke_lambda.ps1
* ./invoke_lambda.ps1

The script invokes the lambda with tests/event.json and prints the JSON response.
Check your e-mail inbox for the SNS notification containing execution details.

Tools & Frameworks Used
AWS CDK (v2, Python) - IaC tool
GitHub Actions - CI/CD Pipeline (manual deploy)
AWS CLI - Local / script based invocation of the lambda function.
boto3 - AWS SDK inside the lambda.