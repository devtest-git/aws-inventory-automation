# aws-inventory-automation
# AWS Inventory Python

Cross-account AWS inventory, backup, and compliance reporting automation using Python and Boto3.

This repository contains Python-based AWS reporting and inventory automation utilities for cloud infrastructure visibility, backup auditing, and operational reporting.

---

# Features

- Cross-account AWS inventory reporting
- IAM AssumeRole support
- EBS volume inventory
- Snapshot tracking and reporting
- EC2 instance mapping
- Private IP visibility
- Encryption and KMS reporting
- CSV-based report generation
- Jenkins automation compatible
- Pagination support for large environments

---

# Current Utilities

## EBS Snapshot Inventory Report

Generates detailed EBS snapshot inventory reports including:

- EC2 Name
- Instance ID
- Private IP
- Volume Name
- Volume ID
- Volume Type
- Device Mapping
- Volume Size
- Encryption Status
- KMS Key
- Snapshot Count
- Latest Snapshot Information
- Snapshot Description

---

# Repository Structure

```text
aws-inventory-python/
│
├── ebs/
│   ├── Backup.py
│   ├── requirements.txt
│   └── sample-output/
│
├── Jenkins/
│   └── Jenkinsfile
│
├── README.md
└── .gitignore
```

---

# Prerequisites

- Python 3.x
- boto3
- botocore
- AWS IAM AssumeRole access

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Usage

```bash
python3 Backup.py \
  --region ap-south-1 \
  --file report.csv \
  --rolearn arn:aws:iam::<account-id>:role/<role-name>
```

---

# Example

```bash
python3 Backup.py \
  --region ap-south-1 \
  --file DPLI-Backup-Report.csv \
  --rolearn arn:aws:iam::764371882145:role/Sify-Reporting-DPLI-ReportingRole
```

---

# Sample Report Columns

| Column | Description |
|---|---|
| S.No | Serial Number |
| Region | AWS Region |
| EC2 Name | Instance Name |
| Instance ID | EC2 Instance ID |
| Private IP | EC2 Private IP |
| Volume Name | EBS Volume Name |
| Volume ID | EBS Volume ID |
| Volume Type | gp2/gp3/io1/etc |
| Device | Attached Device |
| Size (GiB) | Volume Size |
| IOPS | Provisioned IOPS |
| Encrypted | Encryption Status |
| KMS Key ID | KMS Key ARN |
| Created From Snapshot | Source Snapshot |
| Number of Snapshots | Total Snapshot Count |
| Latest Snapshot Date | Latest Snapshot Timestamp |
| Latest Snapshot ID | Latest Snapshot ID |
| Snapshot Description | Snapshot Description |

---

# Jenkins Integration

Example Jenkins shell execution:

```bash
python3 /Report/Backup.py \
  --region ap-south-1 \
  --file /Report/Backups/DPLI/DPLI-Backup-Report-$(date +"%Y-%m-%d").csv \
  --rolearn arn:aws:iam::764371882145:role/Sify-Reporting-Account-ReportingRole
```

---

# IAM Permissions Required

The target IAM role should allow:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVolumes",
        "ec2:DescribeSnapshots",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

The Jenkins or execution account should also have:

```text
sts:AssumeRole
```

permission on the target role.

---

# Future Enhancements

- Multi-region inventory
- Multi-account reporting
- Excel report generation
- Snapshot age analysis
- Orphan EBS detection
- Backup compliance reporting
- AWS Backup integration
- Cost estimation
- Email notifications
- S3 archival
- Dashboard integration

---

# Author

Sandeep Ravindran
Cloud / DevOps Engineer
AWS | Azure | GCP | Terraform | Kubernetes
