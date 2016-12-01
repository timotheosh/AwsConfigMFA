# Class InstanceByRole

from boto.ec2 import connect_to_region
from sys import path
from os import environ
path.append('%s/programs/lib' % environ['HOME'])

from AwsConfigMFA import AwsConfigMFA

class InstanceByTag():
    """
    Do things with instances defined by AWS tags.
    """
    def __init__(self, profile, region='us-east-1', tag=None, value=None, key_name=None):
        """
        @param profile  Profile defined in your AWS config file
                        (Usually the file defined by the environment
                         variable $AWS_CONFIG_FILE. If you omit tag and
                         value parameters, it willcollect all instances
                         that pertain to the profile.

        @param region   The region to connect to.

        @param tag      The tag name to search on. If you omit value
                        it will return all instances with this tag.

        @param value    The value of the specified tag. Specifying this
                        parameter should collect all instances where
                        tag = value.

        @param key_name Filter results

        @var self.instances A list of instances that can be queried in
                            other class functions.
        """
        config = AwsConfigMFA()
        creds = config.getTokenCredentials(profile)
        try:
            conn = connect_to_region(region,
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                security_token = creds['security_token'])
        except Exception,e:
            print "Failed to connect!"
            print e.message

        try:
            self.instances = []
            instances = conn.get_only_instances()
            if not hasattr(key_name, '__iter__'):
                if hasattr(key_name, 'join'):
                    key_name = [key_name]
                else:
                    # Invalid key_name. Just won't say anything to the user =P
                    key_name = None
            if key_name:
                # Return only the instances with key_name(s)
                instances = self.__parse_by_key_names__(instances, key_name)

            if tag:
                for x in instances:
                    if x.tags.has_key(tag):
                        if value:
                            if x.tags[tag] == value:
                                self.instances.append(x)
                        else:
                            self.instances.append(x)
            else:
                self.instances = instances
        except Exception,e:
            print e

    def __parse_by_key_names__(self, instances, key_names):
        rtn = []
        for x in instances:
            if x.key_name in key_names:
                rtn.append(x)
        return rtn

    def private_ips(self, key_name = None):
        l = []
        for x in self.instances:
            if x.private_ip_address:
                if key_name:
                    if x.key_name == key_name:
                        l.append(x.private_ip_address)
                else:
                    l.append(x.private_ip_address)
        return l

    def instance_by_ip(self, private_ip):
        rtn = None
        for x in self.instances:
            if x.private_ip_address == private_ip:
                rtn = x
        return rtn


    def role_by_ip(self, ip):
        rtn = None
        for x in self.instances:
            if x.private_ip_address == ip:
                rtn = x.tags['role']
        return rtn

if __name__ == "__main__":
    s = InstanceByTag('dev', 'us-east-1', 'role', 'public_api')
    print ' '.join(s.private_ips())
