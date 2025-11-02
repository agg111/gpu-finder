"""
AWS EC2 launcher for GPU training jobs.
Launches minimal instances with automatic training and shutdown.
"""
import boto3
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


def ensure_iam_role_with_s3_access(s3_bucket: str, role_name: str = "gpu-finder-ec2-role") -> str:
    """
    Create or update IAM role with S3 write permissions.

    Args:
        s3_bucket: S3 bucket name to grant access to
        role_name: Name of the IAM role to create/update

    Returns:
        Name of the instance profile to use
    """
    iam = boto3.client("iam")

    # Trust policy allowing EC2 to assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # S3 access policy
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:GetObject"
                ],
                "Resource": f"arn:aws:s3:::{s3_bucket}/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": f"arn:aws:s3:::{s3_bucket}"
            }
        ]
    }

    policy_name = f"{role_name}-s3-policy"

    try:
        # Try to create the role
        print(f"[IAM] 🔧 Creating IAM role: {role_name}")
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="GPU Finder EC2 role with S3 access for training logs"
        )
        print(f"[IAM] ✅ IAM role created: {role_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"[IAM] ℹ️  IAM role already exists: {role_name}")

    try:
        # Put/update the inline policy
        print(f"[IAM] 🔧 Attaching S3 policy to role...")
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(s3_policy)
        )
        print(f"[IAM] ✅ S3 policy attached to role")
    except Exception as e:
        print(f"[IAM] ⚠️  Error attaching policy: {e}")

    # Create instance profile if it doesn't exist
    instance_profile_name = role_name
    try:
        print(f"[IAM] 🔧 Creating instance profile: {instance_profile_name}")
        iam.create_instance_profile(
            InstanceProfileName=instance_profile_name
        )
        print(f"[IAM] ✅ Instance profile created")

        # Add role to instance profile
        iam.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName=role_name
        )
        print(f"[IAM] ✅ Role added to instance profile")

        # Wait a bit for IAM to propagate
        import time
        print(f"[IAM] ⏳ Waiting 5 seconds for IAM to propagate...")
        time.sleep(5)

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"[IAM] ℹ️  Instance profile already exists: {instance_profile_name}")
    except Exception as e:
        print(f"[IAM] ⚠️  Error with instance profile: {e}")

    return instance_profile_name


def load_training_script() -> str:
    """Load the training script from file."""
    script_path = os.path.join(os.path.dirname(__file__), "training_script.py")
    with open(script_path, "r") as f:
        return f.read()


def create_user_data_script(
    model_name: str,
    workload: str,
    s3_bucket: Optional[str] = None,
    instance_id_placeholder: str = "INSTANCE_ID"
) -> str:
    """
    Create EC2 user data script that:
    1. Installs Python and PyTorch
    2. Runs training script
    3. Uploads results to S3
    4. Shuts down instance
    """
    training_script = load_training_script()

    s3_upload = ""
    if s3_bucket:
        s3_upload = f"""
# Upload results to S3
echo "📤 Uploading results to S3..."
aws s3 cp /home/ec2-user/training_output.log s3://{s3_bucket}/training-logs/$INSTANCE_ID/output.log
aws s3 cp /home/ec2-user/training_results.json s3://{s3_bucket}/training-logs/$INSTANCE_ID/results.json
echo "✅ Results uploaded to s3://{s3_bucket}/training-logs/$INSTANCE_ID/"
"""

    return f"""#!/bin/bash
set -e

# Log everything to a file
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=========================================="
echo "GPU Finder Training Instance User Data"
echo "Started: $(date)"
echo "=========================================="

# Get instance ID
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
echo "Instance ID: $INSTANCE_ID"

# Update system
echo "📦 Updating system packages..."
yum update -y || echo "Warning: yum update failed, continuing..."

# Install Python 3 and pip
echo "🐍 Installing Python..."
yum install -y python3 python3-pip

# Install PyTorch (CPU version for t3.micro)
echo "🔥 Installing PyTorch..."
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Verify Python and PyTorch installation
echo "✅ Python version: $(python3 --version)"
echo "✅ PyTorch installed: $(python3 -c 'import torch; print(torch.__version__)')"

# Create training script
echo "📝 Creating training script..."
cat > /home/ec2-user/train.py << 'TRAINING_SCRIPT_EOF'
{training_script}
TRAINING_SCRIPT_EOF

# Make sure script is readable
chmod +x /home/ec2-user/train.py
chown ec2-user:ec2-user /home/ec2-user/train.py

# Run training and capture output
echo "🏃 Starting training..."
python3 /home/ec2-user/train.py "{model_name}" "{workload}" 2>&1 | tee /home/ec2-user/training_output.log

# Check training exit code
TRAINING_EXIT_CODE=$?
if [ $TRAINING_EXIT_CODE -eq 0 ]; then
    echo "✅ Training completed successfully!"
else
    echo "❌ Training failed with exit code: $TRAINING_EXIT_CODE"
fi

{s3_upload}

echo "=========================================="
echo "User data script completed: $(date)"
echo "=========================================="

# Shutdown instance after training
echo "🛑 Shutting down instance in 10 seconds..."
sleep 10
shutdown -h now
"""


async def launch_training_instance(
    model_name: str,
    workload: str,
    duration: str,
    budget: Optional[str] = None,
    gpu_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Launch an EC2 instance and start training.

    Args:
        model_name: Name of the model to train
        workload: Workload size
        duration: Training duration in hours
        budget: Optional budget constraint
        gpu_config: Optional GPU configuration from plan

    Returns:
        Dict with instance details and training info
    """
    try:
        # Get AWS configuration from environment
        aws_key_name = os.getenv("AWS_KEY_NAME")  # EC2 SSH key pair name (optional)
        # aws_security_group = os.getenv("AWS_SECURITY_GROUP_ID")
        s3_bucket = os.getenv("AWS_S3_BUCKET")

        # Get IAM role from environment or use default
        aws_iam_role = (os.getenv("AWS_IAM_ROLE") or os.getenv("AWS_IAM_INSTANCE_PROFILE") or "").strip()
        aws_iam_role = aws_iam_role if aws_iam_role else None

        # If S3 bucket is configured, ensure the role has proper S3 permissions
        if s3_bucket and aws_iam_role:
            try:
                # Update existing role with S3 permissions
                print(f"[AWS] 🔧 Updating IAM role '{aws_iam_role}' with S3 permissions...")
                aws_iam_role = ensure_iam_role_with_s3_access(s3_bucket, role_name=aws_iam_role)
            except Exception as e:
                print(f"[AWS] ⚠️  Failed to update IAM role: {e}")
                print(f"[AWS] ⚠️  Proceeding anyway - S3 uploads may fail")
        elif s3_bucket and not aws_iam_role:
            # No role configured, create default one
            try:
                aws_iam_role = ensure_iam_role_with_s3_access(s3_bucket)
            except Exception as e:
                print(f"[AWS] ⚠️  Failed to create IAM role: {e}")
                print(f"[AWS] ⚠️  Will launch without IAM role - S3 uploads will fail")

        # Detect S3 bucket region if bucket is configured
        aws_region = os.getenv("AWS_REGION", "us-west-2")
        if s3_bucket:
            try:
                print(f"[AWS] 🔍 Detecting S3 bucket region for: {s3_bucket}")
                s3_client = boto3.client("s3")
                bucket_location = s3_client.get_bucket_location(Bucket=s3_bucket)
                detected_region = bucket_location.get("LocationConstraint")

                # Note: us-east-1 returns None as LocationConstraint
                if detected_region is None:
                    detected_region = "us-east-1"

                aws_region = detected_region
                print(f"[AWS] ✅ S3 bucket region detected: {aws_region}")
            except Exception as e:
                print(f"[AWS] ⚠️  Could not detect S3 bucket region: {e}. Using default: {aws_region}")

        print(f"[AWS] 🌍 EC2 Region: {aws_region}")
        print(f"[AWS] 🔑 SSH Key: {aws_key_name or 'Not configured (no SSH access)'}")
        # print(f"[AWS] 🛡️  Security Group: {aws_security_group or 'Will use default'}")
        print(f"[AWS] 👤 IAM Role: {aws_iam_role or 'Not configured (instance cannot upload to S3)'}")
        print(f"[AWS] 🪣 S3 Bucket: {s3_bucket or 'Not configured (no log uploads)'}")

        # Initialize EC2 client in the same region as S3 bucket
        ec2 = boto3.client("ec2", region_name=aws_region)

        # Use t3.small for sufficient memory (2GB RAM, ~$0.0208/hour)
        # t3.micro (1GB) runs out of memory when installing PyTorch
        instance_type = "t3.small"

        # Find default VPC and subnet
        print(f"[AWS] 🔍 Finding default VPC...")
        vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])

        if not vpcs["Vpcs"]:
            print(f"[AWS] ⚠️  No default VPC found. Creating one...")
            try:
                # Create default VPC
                create_vpc_response = ec2.create_default_vpc()
                vpc_id = create_vpc_response["Vpc"]["VpcId"]
                print(f"[AWS] ✅ Created default VPC: {vpc_id}")
            except Exception as vpc_error:
                raise Exception(f"No default VPC found and failed to create one: {vpc_error}. Please create a default VPC in your AWS console.")
        else:
            vpc_id = vpcs["Vpcs"][0]["VpcId"]
            print(f"[AWS] ✅ Using default VPC: {vpc_id}")

        # Get a subnet from the default VPC
        subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
        if not subnets["Subnets"]:
            raise Exception(f"No subnets found in VPC {vpc_id}")

        subnet_id = subnets["Subnets"][0]["SubnetId"]
        print(f"[AWS] ✅ Using subnet: {subnet_id}")

        # Get latest Amazon Linux 2023 AMI
        print(f"[AWS] 🔍 Finding latest Amazon Linux 2023 AMI...")
        ami_response = ec2.describe_images(
            Owners=["amazon"],
            Filters=[
                {"Name": "name", "Values": ["al2023-ami-2023.*-x86_64"]},
                {"Name": "state", "Values": ["available"]},
            ]
        )

        if not ami_response["Images"]:
            raise Exception("Could not find Amazon Linux 2023 AMI")

        # Sort by creation date to get the latest
        sorted_images = sorted(ami_response["Images"], key=lambda x: x["CreationDate"], reverse=True)
        ami_id = sorted_images[0]["ImageId"]
        print(f"[AWS] ✅ Using AMI: {ami_id} (created: {sorted_images[0]['CreationDate']})")

        # Create user data script
        user_data = create_user_data_script(model_name, workload, s3_bucket)

        # Prepare launch parameters
        launch_params = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1,
            "UserData": user_data,
            "SubnetId": subnet_id,  # Required when no default VPC
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": f"gpu-finder-training-{model_name}"},
                        {"Key": "Project", "Value": "GPU Finder"},
                        {"Key": "Model", "Value": model_name},
                        {"Key": "LaunchedAt", "Value": datetime.now().isoformat()},
                    ]
                }
            ]
        }

        # Add optional parameters if configured
        if aws_key_name:
            launch_params["KeyName"] = aws_key_name

        # if aws_security_group:
        #     launch_params["SecurityGroupIds"] = [aws_security_group]

        if aws_iam_role:
            launch_params["IamInstanceProfile"] = {"Name": aws_iam_role}

        # Launch instance
        print(f"[AWS] 🚀 Launching {instance_type} instance...")
        response = ec2.run_instances(**launch_params)

        instance_id = response["Instances"][0]["InstanceId"]
        print(f"[AWS] ✅ Instance launched: {instance_id}")

        # Get instance details
        instance = response["Instances"][0]

        result = {
            "status": "success",
            "instance_id": instance_id,
            "instance_type": instance_type,
            "region": aws_region,
            "ami_id": ami_id,
            "model": model_name,
            "workload": workload,
            "estimated_cost": "~$0.02/hour (t3.small, 2GB RAM)",
            "estimated_time": "~2-3 minutes (including startup and training)",
            "message": f"EC2 instance {instance_id} launched successfully. Training will start automatically and instance will shutdown when complete.",
            "dashboard_url": f"https://{aws_region}.console.aws.amazon.com/ec2/v2/home?region={aws_region}#InstanceDetails:instanceId={instance_id}",
            "s3_logs_url": f"https://s3.console.aws.amazon.com/s3/buckets/{s3_bucket}?prefix=training-logs/{instance_id}/" if s3_bucket else None
        }

        print(f"[AWS] 📊 Dashboard: {result['dashboard_url']}")
        if s3_bucket:
            print(f"[AWS] 📦 Logs will be at: s3://{s3_bucket}/training-logs/{instance_id}/")

        return result

    except Exception as e:
        print(f"[AWS] ❌ Error launching instance: {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to launch EC2 instance: {str(e)}"
        }


if __name__ == "__main__":
    # Test the launcher
    import asyncio

    result = asyncio.run(launch_training_instance(
        model_name="test-model",
        workload="100MB",
        duration="1"
    ))

    print(f"\n📋 Result: {result}")
