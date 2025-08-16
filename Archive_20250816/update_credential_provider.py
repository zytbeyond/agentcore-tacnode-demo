#!/usr/bin/env python3
"""
Update the credential provider with the working TACNode token
"""

import boto3
import json

def update_credential_provider():
    """Update the credential provider with working token"""
    print("🔧 UPDATING CREDENTIAL PROVIDER WITH WORKING TOKEN")
    print("=" * 60)
    
    # Working TACNode token
    working_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    secret_arn = "arn:aws:secretsmanager:us-east-1:560155322832:secret:bedrock-agentcore-identity!default/apikey/TACNodeAPIKeyFixed-80wnDj"
    
    print(f"Working Token: {working_token[:50]}...")
    print(f"Secret ARN: {secret_arn}")
    
    try:
        # Update the secret with the working token
        secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
        
        print(f"\n🔄 Updating secret with working token...")
        
        response = secrets_client.update_secret(
            SecretId=secret_arn,
            SecretString=working_token
        )
        
        print(f"✅ Secret updated successfully!")
        print(f"   Version ID: {response.get('VersionId', 'Unknown')}")
        print(f"   ARN: {response.get('ARN', 'Unknown')}")
        
        # Verify the update
        print(f"\n🔍 Verifying secret update...")
        
        verify_response = secrets_client.get_secret_value(SecretId=secret_arn)
        stored_token = verify_response['SecretString']
        
        if stored_token == working_token:
            print(f"✅ Verification successful - token correctly stored")
            print(f"   Stored token: {stored_token[:50]}...")
            return True
        else:
            print(f"❌ Verification failed - token mismatch")
            print(f"   Expected: {working_token[:50]}...")
            print(f"   Stored: {stored_token[:50]}...")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update secret: {e}")
        return False

def main():
    """Update credential provider with working token"""
    print("🔧 CREDENTIAL PROVIDER UPDATE")
    print("=" * 70)
    
    success = update_credential_provider()
    
    if success:
        print(f"\n✅ CREDENTIAL PROVIDER UPDATED SUCCESSFULLY!")
        print(f"✅ Working TACNode token now stored in AWS Secrets Manager")
        print(f"✅ Gateway should now be able to authenticate with TACNode")
        print(f"🧪 Ready to test the complete end-to-end integration")
    else:
        print(f"\n❌ CREDENTIAL PROVIDER UPDATE FAILED")
        print(f"❌ Cannot proceed until credential provider is fixed")

if __name__ == "__main__":
    main()
