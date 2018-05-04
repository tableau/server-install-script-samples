# AWS CloudFormation Templates for TSM Windows
----

For Tableau Services Manager Windows, we are providing a set of sample [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates that can be used as a basis for building your own templates for deploying Tableau Server to Amazon Web Services (AWS).

* **tableau-single-server-windows-tsm.json** is a basic template used to set up a single-node Tableau Server on Windows using Tableau Services Manager.
* **tableau-cluster-windows-tsm-simple.json** is a template used to set up a simple three-node Tableau Server cluster on Windows using Tableau Services Manager.

### Usage

1. On the AWS Management Console go to CloudFormation > Create Stack.
2. Upload the template file > Click Next.
3. Provide a "Stack name" and fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
4. Continue through the rest of the screens and Accept the IAM warning (if applicable) and click Submit.
5. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the PublicDNSName and/or PublicIpAddress.
6. Verify that you can connect to Tableau Server by navigating to the TableauServerURL/LoadBalancerDNSName and logging in with the admin account that you specified.

### General Troubleshooting

To aid in troubleshooting, we suggest disabling automatic rollback of the AWS CloudFormation stack. This allows examination of any log files left in place on the Tableau Server instance(s); rolling back destroys these instances, which means the log files are lost.
