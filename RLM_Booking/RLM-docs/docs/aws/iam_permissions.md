# IAM and Permissions

This document provides an overview of IAM roles and permissions, ensuring secure, role-based access control for the project team.

---

## A. Role-Based Access Control (RBAC)

### Purpose

- Set up IAM roles specific to each team member's function to ensure controlled access to resources.

### Role Assignments

1. **Project Manager Role**: Full administrative access for oversight and management.
   - Assigned to: David
   - Permissions: Full access to all AWS resources for project oversight.
2. **Business Analyst Role**: Limited access for data reporting and analysis.
   - Assigned to: Eli
   - Permissions: Access to Amazon QuickSight, Athena, and read-only permissions for DynamoDB and S3.
3. **Front End Developer Role**: Access for front-end assets and API invocation.
   - Assigned to: Alex
   - Permissions: Read-only access to S3 for assets, view-only access to Lambda functions, and API Gateway invocation permissions.
4. **Back End Developer Role**: Full backend operations access.
   - Assigned to: Michael
   - Permissions: Full access to Lambda, RDS, API Gateway, and DynamoDB as needed.
5. **Data Scientist Role**: Permissions for model development and data processing.
   - Assigned to: Cody
   - Permissions: Full access to SageMaker, Glue, read-only access to DynamoDB, and S3 for data storage.
6. **Data Engineer Role**: Data ingestion and transformation permissions.
   - Assigned to: Andy
   - Permissions: Full access to Glue, Kinesis, S3, and optional DynamoDB for data management.

---

## B. IAM Groups and Policies

1. **DevTeam Group**:
   - All developers are part of the `DevTeam` IAM group, which includes shared permissions like CloudWatch read-only access and S3 read-only access.

2. **Temporary Credentials and Assume Role**:
   - Encouraged my team's developers to use temporary credentials by assuming roles with AWS CLI or SDK to minimize long-term credential exposure.

---

## C. Secrets Management

1. **AWS Secrets Manager**:
   - Used Secrets Manager to store sensitive API keys or credentials securely.
2. **Accessing Secrets Programmatically**:
   - Used SDKs (e.g., Python's boto3) to fetch secrets securely in application code.

---
