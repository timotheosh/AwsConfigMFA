# AwsConfigMFA

Description
==========
This is a python module that will generate multi-factor authentication tokens
for use with Amazon Web Services.

In order to use this, you will need to create a file containing your AWS
access key id, AWS secret access key, and the arn address for your MFA
device. Like below:

```
[profile dev]
mfa_serial_number = arn:aws:iam::121748714988:mfa/joe.schmoe
aws_access_key_id = JBNUJDUJNBUOSUJNSUJSJL
aws_secret_access_key = Rkjgrfww879qwaejfdwe9ZJD89823034123jmjskf
region = us-east-1

[profile test]
mfa_serial_number = arn:aws:iam::029348391284986:mfa/joe.shmoe
aws_access_key_id = KJHIUDHBUDHBNIUDNJSKJJ
aws_secret_access_key = nnnjsjnsew0987JHIJ9KJIKU8787y2hoHNhnuonhuuijjan
region = us-east-1

[profile prod]
mfa_serial_number = arn:aws:iam::927924398723:mfa/joe.shmoe
aws_access_key_id = LKJHNUODILKJNDLOIKDJMD
aws_secret_access_key = vskljnJLKNLOKJ0348924397823JKBJKjlnkacdGFJHN
region = us-east-1
```

The aws_access_key_id and the mfa_serial_number are accessible in the
AWS console (if you have rights to view yourself in the console). The
aws_secret_access_key is only available at key creation time. The
default location that this file is looked for is in
$HOME/.aws/aws_mfa.conf, however you can specify a different location
when you create the AwsConfigMFA object, i.e.:
```python
c = AwsConfig(goldenFile="/home/user/.secret/file")
```

This library reads your current $AWS_CONFIG_FILE like a ini file, and
will preserve any key/value pairs in that file not controlled by this
library (anything other than mfa_serial_number, aws_access_key_id,
aws_secred_access_key, and region). If you want to write your MFA
tokens to a different file, just specify at object creation:
```python
c = AwsConfigMFA(awsConfig="/home/user/my_tokens")
```

If your $AWS_CONFIG_FILE has aged beyond the specified timeout (the
default is 36 hours), it will automatically reprompt you for your MFA
keys to regenerate your tokens. You can specify a different timeout at
object creation with:
```python
c = AwsConfigMFA(token_timeout=12)
```

If you want to force MFA token creation, before the timeout, you can
add the "force=True" parameter:
```python
c = AwsConfigMFA(force=True)
```

You can also specify multiple options at once at object creation. i.e.:
```python
c = AwsConfigMFA(awsConfig="/home/user/my_tokens",
                 goldenFile="/home/user/perma_stuff",
                 force=True,
                 token_timeout = 12)
```

Sample usage with Boto:
```python
from boto import connect_ec2
from AwsConfigMFA import AwsConfigMFA

c = AwsConfigMFA()
creds = c.getTokenCredentials('dev')
conn = connect_ec2(creds['access_key'],
                   creds['secret_key'],
                   security_token = creds['session_token'])
instances = conn.get_only_instances()
```

