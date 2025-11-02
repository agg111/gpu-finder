#!/usr/bin/env python3
"""
Script to check EC2 instance logs and status.
"""
import boto3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_instance_status(instance_id):
    """Check the status and logs of an EC2 instance."""

    # Detect S3 bucket region
    s3_bucket = os.getenv("AWS_S3_BUCKET")
    if s3_bucket:
        try:
            s3_client = boto3.client("s3")
            bucket_location = s3_client.get_bucket_location(Bucket=s3_bucket)
            region = bucket_location.get("LocationConstraint")
            if region is None:
                region = "us-east-1"
        except Exception as e:
            print(f"Warning: Could not detect S3 bucket region: {e}")
            region = os.getenv("AWS_REGION", "us-west-2")
    else:
        region = os.getenv("AWS_REGION", "us-west-2")

    print(f"Using region: {region}")
    ec2 = boto3.client("ec2", region_name=region)

    try:
        # Get instance details
        print(f"\n📊 Checking instance: {instance_id}")
        response = ec2.describe_instances(InstanceIds=[instance_id])

        if not response["Reservations"]:
            print(f"❌ Instance {instance_id} not found in region {region}")
            return

        instance = response["Reservations"][0]["Instances"][0]

        print(f"\n✅ Instance State: {instance['State']['Name']}")
        print(f"   Instance Type: {instance['InstanceType']}")
        print(f"   Launch Time: {instance['LaunchTime']}")

        if 'PublicIpAddress' in instance:
            print(f"   Public IP: {instance['PublicIpAddress']}")

        # Get console output (system logs)
        print(f"\n📜 Fetching console output (system logs)...")
        try:
            console_output = ec2.get_console_output(InstanceId=instance_id)

            if 'Output' in console_output:
                output = console_output['Output']
                print("\n" + "="*80)
                print("CONSOLE OUTPUT (Last 100 lines):")
                print("="*80)
                lines = output.split('\n')
                for line in lines[-100:]:
                    print(line)
                print("="*80)
            else:
                print("⚠️  No console output available yet. The instance may still be starting up.")
                print("   Wait 1-2 minutes and try again.")
        except Exception as e:
            print(f"⚠️  Could not fetch console output: {e}")

        # Check if instance has stopped
        if instance['State']['Name'] == 'stopped':
            print("\n✅ Instance has stopped (training completed)")
            print(f"   Check S3 for logs: s3://{s3_bucket}/training-logs/{instance_id}/")
        elif instance['State']['Name'] == 'running':
            print("\n🏃 Instance is still running (training may be in progress)")
            print("   Wait a few more minutes for completion")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_instance_logs.py <instance-id>")
        print("Example: python3 check_instance_logs.py i-044ce711e6d32cf15")
        sys.exit(1)

    instance_id = sys.argv[1]
    check_instance_status(instance_id)
