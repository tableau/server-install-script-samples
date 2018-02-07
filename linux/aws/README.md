# AWS CloudFormation Templates for Linux
----

For Linux, we are providing a set of sample [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates that can be used as a basis for building your own templates for deploying a fully functional Tableau Server to Amazon Web Services (AWS), following best practices from AWS and Tableau Software.  This repository contains AWS CloudFormation templates to automatically deploy a standalone or cluster (distributed) architecture for Tableau Server into your AWS account.

For detailed information about deploying Tableau Server on AWS using these templates, view the [AWS Cloud deployment guide](https://onlinehelp.tableau.com/v10.5/offline/en-us/tableau-server-on-the-aws-cloud_linux.pdf). 

### Standalone Templates
* **tableau-single-server-centos.json** is a basic template used to set up a single-node Tableau Server on Linux CentOS.
* **tableau-single-server-ubuntu.json** is a basic template used to set up a single-node Tableau Server on Linux Ubuntu.

### Cluster Templates
* **tableau-cluster-server-linux-simple.json** is a template used to set up a simple three-node Tableau Server cluster on Linux CentOS.
* **tableau-cluster-server-linux-existing-vpc.json** is a template for an advanced setup of a three-node Tableau Server cluster on Linux CentOS or Ubuntu into an existing VPC with 3 private subnets.

### Usage

1. On the AWS Management Console go to CloudFormation > Create Stack.
2. Upload the template file > Click Next.
3. Provide a "Stack name" and fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
4. Continue through the rest of the screens and Accept the IAM warning (if applicable) and click Submit.
5. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the PublicDNSName and/or PublicIpAddress.
6. Verify that you can connect to Tableau Server by navigating to the TableauServerURL/LoadBalancerDNSName and logging in with the admin account that you specified.

#### Optional for Cluster Deployment:

To improve the security of your Tableau Server installation, Tableau recommends the use of SSL for protected communication with clients. Note that all examples that use SSL assume the use of AWS Certificate Manager and Amazon Route53.  When launching the stack, provide the following additional information:

* Provide the ARN (Amazon Resource Name) for the SSL certificate you wish to use. (See AWS Certificate Manager in the AWS Management Console.)
* Provide the fully qualified host name (FQHN) for your new server; this MUST match the name in the SSL certificate you are using!
* Provide the hosted zone id (in Route53) in which you'd like to create the server. You'll be provided a list of potential zones; remember to pick one that works with the SSL cert and FQHN you're using.

### General Troubleshooting

To aid in troubleshooting, we suggest disabling automatic rollback of the AWS CloudFormation stack. This allows examination of any log files left in place on the Tableau Server instance(s); rolling back destroys these instances, which means the log files are lost.
