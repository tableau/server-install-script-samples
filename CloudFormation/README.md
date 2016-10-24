# AWS CloudFormation Templates
----

We are providing a set of sample [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates that can be used as a basis for building your own templates for deploying Tableau Server to Amazon Web Services (AWS).

* **[public-sample-single-server.cfn:](#SimpleSingleNode)** A very basic template used to set up a simple single-node Tableau Server.
* **[public-ssl-single-server.cfn:](#SecureSingleNode)** A simple template used to set up a simple single-node Tableau Server that uses SSL for protected communication with clients.
* **[public-ssl-cluster-server.cfn:](#SecureClusterNode)** A template used to set up a simple three-node Tableau Server cluster that uses SSL for protected communication with clients.

To improve the security of your Tableau Server installation, Tableau recommends the use of SSL for protected communication with clients. Note that all examples that use SSL assume the use of AWS Certificate Manager and Amazon Route53. 

### Requirements
* You must have your own provisioned AWS account.
* You must have an [Amazon Elastic Compute Cloud (Amazon EC2) key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).
* You must create a named [Amazon S3](https://aws.amazon.com/s3/) bucket containing the following items:
	* A copy of [ScriptedInstaller.py](../ScriptedInstaller.py)
	* A copy of the Tableau Server installer (v10.1 or higher)
	* A copy of the Tableau Server worker installer (v10.1 or higher) *(Required for distributed installations-only)*
* *(Optional)* A domain managed by [Amazon Route53](https://aws.amazon.com/route53/). *(Required for the SSL examples)*
* *(Optional)* An SSL certificate managed by [AWS Certificate Manager](https://aws.amazon.com/certificate-manager/) in the region in which you are deploying *(Required for the SSL examples)*


### General Troubleshooting

To aid in troubleshooting, we suggest disabling automatic rollback of the AWS CloudFormation stack. This allows examination of any log files left in place on the Tableau Server instance(s) ; rolling back destroys these instances, which means the log files are lost.

## <a name="SimpleSingleNode"></a>public-sample-single-server.cfn

This is a simple AWS CloudFormation Template for automating the deployment of Tableau Server to AWS.  This AWS CloudFormation template will deploy a default single-node instance using local authentication and default configurations.  The template allows for minimal customization of the Gateway port and process counts on the server.

**Time to Deploy:** Approximately 30 minutes.

### Usage

1. On the AWS Management Console go to CloudFormation > Create Stack.
2. Select the template file (public-sample-single-server.cfn) > Click Next.
3. Provide a "Stack name" and fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
4. Continue through the rest of the screens and Accept the IAM warning and click Submit.
5. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the PublicDNSName and/or PublicIpAddress.
6. Verify that you can connect to Tableau Server by navigating to the PublicDNSName/PublicIpAddress and logging in with the admin account that you specified.

### Known Issues/Troubleshooting Steps

None as of this writing.


## <a name="SecureSingleNode"></a>public-sample-ssl-single-server.cfn

This is an AWS CloudFormation Template for automating the deployment of a single-node instance of Tableau Server to AWS configured with external SSL. This template will deploy a default single-node instance using local authentication and default configurations.  The template allows for minimal customization of the Gateway port and process counts on the server.  In addition, the server will be reachable via an encrypted connection, using the SSL certificate

The use of this template assumes the user users Route53 for managing their DNS, and the user has an SSL certificate managed by AWS Certificate Manager.

**Time to Deploy:** Approximately 35 minutes.

### Usage

1. On the AWS Management Console go to CloudFormation > Create Stack.
2. Select the template file (public-sample-ssl-single-server.cfn) > Click Next.
3. Provide a "Stack name" 
4. Provide the ARN (Amazon Resource Name) for the SSL certificate you wish to use. (See AWS Certificate Manager in the AWS Management Console.)
5. Provide the fully qualified host name (FQHN) for your new server; this MUST match the name in the SSL certificate you are using!
6. Provide the hosted zone id (in Route53) in which you'd like to create the server. You'll be provided a list of potential zones; remember to pick one that works with the SSL cert and FQHN you're using.
7. Fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
8. Continue through the rest of the screens and Accept the IAM warning and click Submit.
9. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the SSLDNSName (used to connect to the Tableau Server web interface) and InstanceDNSName (used to Remote Desktop to the Windows instance)
10. Verify that you can connect to Tableau Server by navigating to the SSLDNSName and logging in with the admin account that you specified.

### Known Issues/Troubleshooting Steps

None as of this writing.


## <a name="SecureClusterNode"></a>public-sample-ssl-cluster.cfn

This is a sample AWS CloudFormation Template for automating the deployment of a Tableau Server cluster to AWS.  This AWS CloudFormation template will deploy a relatively simple three-node cluster using local authentication and default configurations into a private subnet, with an additional bastion host usable to access the three server nodes. The server web interface will be reachable via an encrypted connection, using the SSL certificate attached to a load balancer.

The AWS CloudFormation template generates the config file used to specificy the number of various processes running on the various cluster members; these settings can be tweaked by editing the AWS CloudFormation template to change the values or by adding parameters used as input to the script. (See [public-sample-single-server.cfn](#SimpleSingleNode) as an example.)

The use of this template assumes the user has Route53 managing their DNS, and the user has an SSL certificate being managed by AWS Certificate Manager.

**Time to Deploy:** Approximately 50 minutes.

### Usage

1. On the AWS Management Console go to CloudFormation > Create Stack.
2. Select the template file (public-sample-ssl-cluster.cfn) > Click Next.
3. Provide a "Stack name" 
4. Provide the ARN to the SSL certificate you wish to use (see AWS Certificate Manager in the AWS Management Console)
5. Provide the fully qualified host name for your new server; this MUST match the name in the SSL certificate you are using!
6. Provide the hosted zone id (in Route53) in which you'd like to create the server. You'll be provided a list of potential zones; remember to pick one that works with the SSL cert and FQHN you're using.
7. Fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
8. Continue through the rest of the screens and Accept the IAM warning and click Submit.
9. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the SSLDNSName (used to connect to the Tableau Server web interface) and BastionDNSName(used to Remote Desktop to the Windows bastion host; from there, you can RDP into the Tableau Server instances).
10. Verify that you can connect to Tableau Server by navigating to the SSLDNSName and logging in with the admin account that you specified.

### Known Issues/Troubleshooting Steps

Occasionally, instance-to-instance networking speed may be slow during setup; this could cause timeouts to trigger an abort scenario. One can workaround this problem by increasing the timeout specified for the TableauPrimaryWaitCondition resource in the AWS CloudFormation template.


