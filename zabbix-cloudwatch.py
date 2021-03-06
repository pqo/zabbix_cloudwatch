#!/usr/bin/python2.7

import argparse
import boto
import boto.ec2.elb
import boto.rds
from boto.ec2.cloudwatch import CloudWatchConnection
from boto.ec2 import *
import datetime
import os, time
import json

#amazon uses UTC at cloudwatch
os.environ['TZ'] = 'UTC'
time.tzset()

parser = argparse.ArgumentParser(description='Zabbix CloudWatch client')

parser.add_argument('-a', '--account', dest='account', help='Account', required=True)
parser.add_argument('-r', '--region', dest='region', default='us-east-1', help='AWS region')
parser.add_argument('-d', '--dimension', dest='dimension',
                  default=None, help='Cloudwatch Dimension')
parser.add_argument('-n', '--namespace', dest='namespace',
                  default='AWS/EC2', help='Cloudwatch Namespace')
parser.add_argument('-m', '--metric', dest='metric',
                  default='NetworkOut', help='Cloudwatch Metric')
parser.add_argument('-s', '--statistic', dest='statistic',
                  default='Sum', help='Cloudwatch Statistic')
parser.add_argument('-i', '--interval', dest='interval',
                  type=int,default=60, help='Interval')
parser.add_argument('-D', '--discovery', dest='discovery',
                  choices=['ELB','RDS'], help='Run Discovery')
parser.add_argument('-l', '--elb', dest='elb',
                  help='ELB to discover instances for')
parser.add_argument('-v', '--verbose', action='count', dest='verbose')

args = parser.parse_args()

if args.account == 'zabbix':
    aws_key = '<%= @aws_key %>' #YOUR_AWS_KEY_GOES_HERE
    aws_secret = '<%= @aws_secret %>' #YOUR_AWS_SECRET_GOES_HERE
elif args.account == '<%= @aws_account2 %>':
    aws_key = '<%= @aws_key2 %>'
    aws_secret = '<%= @aws_secret2 %>'

if args.discovery:
  if 'ELB' in args.discovery:
    conn = boto.ec2.elb.connect_to_region(args.region,
                                          aws_access_key_id=aws_key,
                                          aws_secret_access_key=aws_secret)

    elbRetData = { "data": [ ] }
    if args.elb:
      ec2_connection = boto.ec2.connection.EC2Connection(
                                          aws_access_key_id=aws_key,
                                          aws_secret_access_key=aws_secret)


      for elb_name in args.elb.split(':'):
        elb_data = conn.get_all_load_balancers(load_balancer_names=[elb_name])[0]

        instance_ids = [ instance.id for instance in elb_data.instances ]
        reservations = ec2_connection.get_all_instances(instance_ids)

        for r in reservations:
          for i in r.instances:
            elbRetData['data'].append(
              {
                '{#LOADBALANCERNAME}': elb_data.name,
                '{#INSTANCEID}': i.id,
                '{#INSTANCEADDRESS}': i.private_dns_name+':'+str(elb_data.listeners[0][1])
              }
            )

    else:
      elbs = conn.get_all_load_balancers()
      for elb in elbs:
        elbRetData['data'].append(
          { '{#LOADBALANCERNAME}': 'LoadBalancerName='+elb.name }
        )

    print json.dumps(elbRetData, indent=4)
  elif 'RDS' in args.discovery:
    conn = boto.rds.connect_to_region(args.region,
                                          aws_access_key_id=aws_key,
                                          aws_secret_access_key=aws_secret)

    rdsRetData = { "data": [ ] }
    rdss = conn.get_all_dbinstances()
    for rds in rdss:
      rdsRetData['data'].append(
      { '{#RDSID}': rds.id }
      )
    print json.dumps(rdsRetData, indent=4)
else:
  end_time = datetime.datetime.now()

  # adding 65 seconds due amazon caracteristic
  end_time = end_time - datetime.timedelta(seconds=65)

  start_time = end_time - datetime.timedelta(seconds=args.interval)

  if args.verbose:
    debug=args.verbose
  else:
    debug=0

  cloudwatch = boto.ec2.cloudwatch.connect_to_region(args.region,
                                    aws_access_key_id=aws_key,
                                    aws_secret_access_key=aws_secret,
                                    is_secure=True,
                                    debug=debug)

  cloudwatch_result = None

  if args.dimension:
      dimension = {}
      dimensions = args.dimension.split('=')
      dimension[dimensions[0]] = dimensions[1]
      cloudwatch_result = cloudwatch.get_metric_statistics(args.interval, start_time, end_time, args.metric, args.namespace, args.statistic, dimensions=dimension)
      if args.verbose:
        print "DEBUG:", cloudwatch_result
  else:
      cloudwatch_result = cloudwatch.get_metric_statistics(args.interval, start_time, end_time, args.metric, args.namespace, args.statistic)

  if len(cloudwatch_result)>0:
    cloudwatch_result = cloudwatch_result[0]
    cloudwatch_result = float(cloudwatch_result[args.statistic])
  else:
    # Return -1 if AWS returned empty list
    cloudwatch_result = -1

  print cloudwatch_result
