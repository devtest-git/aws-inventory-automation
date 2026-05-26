import argparse
import boto3
import csv
from botocore.exceptions import ClientError


def assume_role(role_arn, region):

    sts = boto3.client("sts", region_name=region)

    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="EBSReportSession"
    )

    creds = response["Credentials"]

    ec2_client = boto3.client(
        "ec2",
        region_name=region,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"]
    )

    return ec2_client


def get_instance_details(ec2_client):

    """
    Creates instance lookup:
    {
        instance_id: {
            "name": "server1",
            "private_ip": "10.x.x.x"
        }
    }
    """

    instance_map = {}

    paginator = ec2_client.get_paginator("describe_instances")

    for page in paginator.paginate():

        for reservation in page["Reservations"]:

            for instance in reservation["Instances"]:

                instance_id = instance["InstanceId"]

                ec2_name = next(
                    (
                        tag["Value"]
                        for tag in instance.get("Tags", [])
                        if tag["Key"] == "Name"
                    ),
                    "N/A"
                )

                private_ip = instance.get(
                    "PrivateIpAddress",
                    "N/A"
                )

                instance_map[instance_id] = {
                    "name": ec2_name,
                    "private_ip": private_ip
                }

    return instance_map


def get_snapshot_details(ec2_client, volume_id):

    snapshots = ec2_client.describe_snapshots(
        OwnerIds=["self"],
        Filters=[
            {
                "Name": "volume-id",
                "Values": [volume_id]
            }
        ]
    )["Snapshots"]

    if not snapshots:

        return {
            "count": 0,
            "latest_snapshot": None
        }

    snapshots_sorted = sorted(
        snapshots,
        key=lambda x: x["StartTime"]
    )

    return {
        "count": len(snapshots_sorted),
        "latest_snapshot": snapshots_sorted[-1]
    }


def generate_report(region, role_arn):

    ec2_client = assume_role(role_arn, region)

    instance_map = get_instance_details(ec2_client)

    paginator = ec2_client.get_paginator("describe_volumes")

    report_data = []

    serial_number = 1

    for page in paginator.paginate():

        for volume in page["Volumes"]:

            volume_id = volume["VolumeId"]

            volume_name = next(
                (
                    tag["Value"]
                    for tag in volume.get("Tags", [])
                    if tag["Key"] == "Name"
                ),
                "N/A"
            )

            volume_type = volume["VolumeType"]

            volume_size = volume["Size"]

            iops = volume.get("Iops", "N/A")

            encrypted = "Yes" if volume["Encrypted"] else "No"

            kms_key = volume.get("KmsKeyId", "N/A")

            created_from_snapshot = volume.get(
                "SnapshotId",
                "N/A"
            )

            # Attachment Details
            if volume["Attachments"]:

                attachment = volume["Attachments"][0]

                instance_id = attachment.get(
                    "InstanceId",
                    "N/A"
                )

                device_name = attachment.get(
                    "Device",
                    "N/A"
                )

                instance_details = instance_map.get(
                    instance_id,
                    {}
                )

                ec2_name = instance_details.get(
                    "name",
                    "N/A"
                )

                private_ip = instance_details.get(
                    "private_ip",
                    "N/A"
                )

            else:

                instance_id = "N/A"
                device_name = "N/A"
                ec2_name = "N/A"
                private_ip = "N/A"

            # Snapshot Details
            snapshot_details = get_snapshot_details(
                ec2_client,
                volume_id
            )

            snapshot_count = snapshot_details["count"]

            latest_snapshot = snapshot_details[
                "latest_snapshot"
            ]

            if latest_snapshot:

                snapshot_id = latest_snapshot[
                    "SnapshotId"
                ]

                snapshot_date = latest_snapshot[
                    "StartTime"
                ].strftime("%d-%m-%Y %H:%M")

                snapshot_description = latest_snapshot.get(
                    "Description",
                    ""
                )

            else:

                snapshot_id = "N/A"
                snapshot_date = "N/A"
                snapshot_description = "No Snapshot Found"

            report_data.append({

                "S.No": serial_number,

                "Region": region,

                "EC2 Name": ec2_name,

                "Instance ID": instance_id,

                "Private IP": private_ip,

                "Volume Name": volume_name,

                "Volume ID": volume_id,

                "Volume Type": volume_type,

                "Device": device_name,

                "Size (GiB)": volume_size,

                "IOPS": iops,

                "Encrypted": encrypted,

                "KMS Key ID": kms_key,

                "Created From Snapshot": created_from_snapshot,

                "Number of Snapshots": snapshot_count,

                "Latest Snapshot Date": snapshot_date,

                "Latest Snapshot ID": snapshot_id,

                "Snapshot Description": snapshot_description

            })

            serial_number += 1

    return report_data


def write_report(data, file_path):

    fieldnames = [

        "S.No",

        "Region",

        "EC2 Name",

        "Instance ID",

        "Private IP",

        "Volume Name",

        "Volume ID",

        "Volume Type",

        "Device",

        "Size (GiB)",

        "IOPS",

        "Encrypted",

        "KMS Key ID",

        "Created From Snapshot",

        "Number of Snapshots",

        "Latest Snapshot Date",

        "Latest Snapshot ID",

        "Snapshot Description"
    ]

    with open(file_path, "w", newline="") as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in data:
            writer.writerow(row)


def main():

    parser = argparse.ArgumentParser(
        description="Generate EBS Snapshot Report"
    )

    parser.add_argument(
        "--region",
        required=True,
        help="AWS Region"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="CSV output file"
    )

    parser.add_argument(
        "--rolearn",
        required=True,
        help="IAM Role ARN"
    )

    args = parser.parse_args()

    try:

        data = generate_report(
            args.region,
            args.rolearn
        )

        write_report(
            data,
            args.file
        )

        print(
            f"Report generated successfully: {args.file}"
        )

    except ClientError as e:

        print(f"AWS Error: {e}")

    except Exception as e:

        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
