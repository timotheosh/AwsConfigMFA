#!/usr/bin/env python2.7

from os import environ, stat,  access, R_OK, W_OK
from time import localtime, mktime
from ConfigParser import ConfigParser
from boto import connect_sts

class AwsConfigMFA(ConfigParser):
    def __init__(self, awsConfig=None, goldenFile=None, force = False, token_timeout = 36):
        """
        @params awsConfig      Path to the AWS Config file (default:
                               $HOME/.aws/config)

        @params goldenFile     Path to file containing the arn address
                               for MFA tokens and the permanent AWS
                               keys

        @params force          Will not update the MFA tokens unless
                               the AWS config file is older than
                               the token_timeout, or if force = True.

        @params token_trimeout Timeout for the requested MFA session
                               tokens.
        """
        ConfigParser.__init__(self)
        self.token_timeout = token_timeout
        if not awsConfig:
            awsConfig = "%s/.aws/config" % environ['HOME']
            if environ.has_key('AWS_CONFIG_FILE'):
                awsConfig = environ['AWS_CONFIG_FILE']
        if not goldenFile:
            goldenFile = "%s/.aws/aws_mfa.conf" % environ['HOME']
        msg = self.__testFiles__(awsConfig, goldenFile)
        if len(msg) == 0:
            self.awsConfig = awsConfig
            self.read(awsConfig)
            if self.__checkAge__(awsConfig) > self.token_timeout:
                print "Your %s file is over %d hours old" % (awsConfig, self.token_timeout)
                response = raw_input("Would you like to update tokens now? [Y/n] ")
                if len(response) > 0 and (response[0] == 'n' or response[0] == 'N'):
                    pass
                else:
                    self.updateTokens(goldenFile)
            elif force:
                self.updateTokens(goldenFile)
        else:
            print msg

    def __testFiles__(self, awsConfig, goldenFile):
        msg = ""
        if not access(awsConfig, R_OK):
            msg += "You did not specify a valid aws config file: %s.\n" % awsConfig
            msg += "Be sure to check file permissions, and that the file exists.\n"
        if not access(goldenFile, W_OK):
            msg += "You did not specify a valid aws golden file.\n"
            msg += "Be sure to check file permissions, and that the file exists.\n"
        return msg

    def __checkAge__(self, file):
        lastAccess = stat(file).st_mtime
        now = mktime(localtime())
        return (now - lastAccess) / 60 / 60

    def __getMfaSerial__(self, goldenFile):
        parser = ConfigParser()
        try:
            parser.read(goldenFile)
        except:
            print "ERROR: Cannot read file for mfa serial numbers: %s" % goldenFile
            return None

        serials = {}
        for x in parser.sections():
            vals = {}
            s = x.split()
            key = s[0]
            if len(s) > 1:
                key = s[1]
            if (parser.has_option(x, 'mfa_serial_number')
                and parser.has_option(x, 'aws_access_key_id')
                and parser.has_option(x, 'aws_secret_access_key')):
                    vals.update({'mfa_serial_number': parser.get(x, 'mfa_serial_number')})
                    vals.update({'aws_access_key_id': parser.get(x, 'aws_access_key_id')})
                    vals.update({'aws_secret_access_key': parser.get(x, 'aws_secret_access_key')})
                    vals.update({'region': parser.get(x, 'region')})
                    serials.update({key: vals})
            else:
                print """
SKIPPING %s: There is incomplete information. Make sure all fields are present:
  Fields should include: mfa_serial_number
                         aws_access_key_id
                         aws_secret_access_key
                """ % x
        return serials

    def listSections(self):
        sections = []
        i = 0
        for x in self.sections():
            vals = x.split()
            if len(vals) > 1:
                i += 1
                sections.append({'num': i, 'name': vals[1], 'value': x})

        print "You have a default section defined."
        while 1:
            print "Which of the following sections is your default?"
            for y in sections:
                print "%s) %s" % (y['num'], y['name'])
            try:
                choice = int(raw_input("? ")) - 1
                if choice <= len(sections):
                    return sections[choice]['value']
                else:
                    print ""
                    print "That was not one of the choices"
                    print "NOTE: if you pick none, no tokens will be generated for your default profile."
                    response = raw_input("Do you wish to cancel choosing a default? [Y/n] ")
                    if len(response) > 1 and response[0] != 'N' and response[0] != 'n':
                        return None
            except ValueError:
                print "ERROR: Entry must be a number."

    def __setDefault__(self, default):
        for x in self.options(default):
            self.set('default', x, self.get(default, x))

    def updateTokens(self, goldenFile):
        print "Updating tokens..."
        mfaSerials = self.__getMfaSerial__(goldenFile)
        default = None
        print self.sections()
        for x in self.sections():
            vals = x.split()
            if x == vals[0]:
                print "%s: %s" % (x, vals[0])
                default = self.listSections()
            else:
                section = vals[1]
                credentials = mfaSerials[section]
                timeout = self.token_timeout * 60 * 60
                msg = "Updating token for %s" % section
                if default == section:
                    msg += " and for default"
                mfa = raw_input("MFA for %s: " % section)
                sts = connect_sts(aws_access_key_id = credentials['aws_access_key_id'],
                                  aws_secret_access_key = credentials['aws_secret_access_key'])
                token = sts.get_session_token(duration = timeout, force_new = True,
                                          mfa_serial_number = credentials['mfa_serial_number'], mfa_token = mfa)
                self.set(x, 'aws_access_key_id', token.access_key)
                self.set(x, 'aws_secret_access_key', token.secret_key)
                self.set(x, 'aws_session_token', token.session_token)
                self.set(x, 'region', credentials['region'])
        if default:
            self.__setDefault__(default)
        with open(self.awsConfig, 'wb') as configfile:
            self.write(configfile)

    def getTokenCredentials(self, profile='default'):
        """
        Returns a dictionary object with:
           { 'aws_access_key_id': 'XXXXX',
             'aws_secret_access_key': 'XXXXX',
             'aws_session_token': 'XXXXXXXXXXXXXXXXX'}
        Tries to handle missing values.
        """
        """
        This is to accomodate the possibility of having a section called:
        [Profile default], [profile default], or just [default].
        """
        rtn = {}
        section = None
        for x in self.sections():
            vals = x.split()
            if profile in vals:
              section = ' '.join(vals)
              break
        rtn.update({'access_key': self.get(section, 'aws_access_key_id')})
        rtn.update({'secret_key': self.get(section, 'aws_secret_access_key')})
        rtn.update({'session_token': self.get(section, 'aws_session_token')})
        return rtn

if __name__ == "__main__":
    config = AwsConfigMFA()
    credentials = config.getTokenCredentials('dev')
    print credentials
