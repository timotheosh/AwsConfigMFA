# Class InstanceByRole

from boto import connect_ec2
from sys import path
from os import environ
path.append('%s/programs/lib' % environ['HOME'])

from AwsConfig import AwsConfig

class InstanceByRole():
    """
    Do things with instances defined by AWS role tag.
    """
    def __init__(self, profile, role=None):
        config = AwsConfig()
        creds = config.getTokenCredentials(profile)
        self.role = role
        try:
            conn = connect_ec2(creds['access_key'],
                               creds['secret_key'],
                               security_token = creds['session_token'])
        except:
            print "Failed to connect!"

        try:
            self.instances = []
            instances = conn.get_only_instances()
            if role:
                for x in instances:
                    if x.tags.has_key('role') and x.tags['role'] == role:
                        self.instances.append(x)
            else:
                self.instances = instances
        except Exception,e:
            print e

    def private_ips(self):
        l = []
        for x in self.instances:
            if x.private_ip_address:
                l.append(x.private_ip_address)
        return l

if __name__ == "__main__":
    s = InstanceByRole('dev', 'public_api')
    print ' '.join(s.private_ips())
