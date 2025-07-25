import aws_cdk as core
import aws_cdk.assertions as assertions

from nice_home_assignment.nice_home_assignment_stack import NiceHomeAssignmentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in nice_home_assignment/nice_home_assignment_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = NiceHomeAssignmentStack(app, "nice-home-assignment")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
