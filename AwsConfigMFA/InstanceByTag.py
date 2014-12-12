# Class InstanceByRole

from boto import connect_ec2
from sys import path
from os import environ
path.append('%s/programs/lib' % environ['HOME'])

from AwsConfigMFA import AwsConfigMFA

class InstanceByTag():
    """
    Do things with instances defined by AWS tags.
    """
    def __init__(self, profile, tag=None, value=None):
        config = AwsConfigMFA()
        creds = config.getTokenCredentials(profile)
        try:
            conn = connect_ec2(creds['access_key'],
                               creds['secret_key'],
                               security_token = creds['session_token'])
        except:
            print "Failed to connect!"

        try:
            self.instances = []
            instances = conn.get_only_instances()
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

if __name__ == "__main__":
    s = InstanceByTag('dev', 'role', 'public_api')
    print ' '.join(s.private_ips())
