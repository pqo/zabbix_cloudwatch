#Zabbix CloudWatch and ELB

Zabbix template for AWS CloudWatch monitoring.

CloudWatch template comes with some default items including AutoScaling, RDS, and ELB.

It supports low-level discovery of AWS EC2 ELB and RDS instances and will assign items/triggers to each.


## Install
This is installed on any host with a running Zabbix agent from which you would like to access AWS Cloudwatch API. Typically you'd run this on a Zabbix Server or Proxy.

```
$ git clone https://github.com/pqo/zabbix_cloudwatch
$ cd zabbix_cloudwatch
$ cp zabbix-cloudwatch.py /etc/zabbix/externalscripts/zabbix-cloudwatch.py && chmod 755 /etc/zabbix/externalscripts/zabbix-cloudwatch.py
$ cp cloudwatch.conf /etc/zabbix/zabbix_agentd.conf.d

```
Make sure this line is present in the Zabbix agent configuration file:

```
Include=/etc/zabbix/zabbix_agentd.conf.d/
```

## AWS Configuration

In IAM, create user and attach AmazonEC2ReadOnlyAccess, CloudWatchReadOnlyAccess, and AmazonRDSReadOnlyAccess.
Save user key and secret, you'll need it later.

## Script configuration

Edit zabbix-cloudwatch.py and add previously acquired key/secret to the aws_key and aws_secret variables.

## Zabbix Configuration

* Import template into Zabbix in the Template section of the web GUI
* Add the template to the host
* Add {$MYACCOUNT} macro to the host with value "zabbix"
* Add {$REGION} macro to the host with desired value (example: "us-west-2")

This code is built on
https://github.com/lorieri/zabbix/blob/master/chef/cookbooks/zabbix-aws/templates/default/cloudwatch/zabbix-cloudwatch.py.erb
