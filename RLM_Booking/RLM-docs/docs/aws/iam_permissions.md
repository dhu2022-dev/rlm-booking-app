# IAM and Permissions

This document provides an overview my team's IAM roles and permissions. The aim is to build secure, role-based access control for each member of the project.

---

## A. Role-Based Access Control (RBAC)

### Purpose

- IAM roles specific to each team member's function ensures controlled access to resources.

### Role Assignments

- **Project Manager Role**: Full administrative access for oversight and management.

    - Assigned to: David
    - Permissions: Full access to all AWS resources for project oversight.

- **Business Analyst Role**: Limited access for data reporting and analysis.

    - Assigned to: Eli
    - Permissions: Access to Amazon QuickSight, Athena, and read-only permissions for DynamoDB and S3.

- **Front End Developer Role**: Access for front-end assets and API invocation.

    - Assigned to: Alex
    - Permissions: Read-only access to S3 for assets, view-only access to Lambda functions, and API Gateway invocation permissions.

- **Back End Developer Role**: Full backend operations access.

    - Assigned to: Michael
    - Permissions: Full access to Lambda, RDS, API Gateway, and DynamoDB as needed.

- **Data Scientist Role**: Permissions for model development and data processing.

    - Assigned to: Cody
    - Permissions: Full access to SageMaker, Glue, read-only access to DynamoDB, and S3 for data storage.

- **Data Engineer Role**: Data ingestion and transformation permissions.

    - Assigned to: Andy
    - Permissions: Full access to Glue, Kinesis, S3, and optional DynamoDB for data management.

---

## B. IAM Groups and Policies

- **DevTeam Group**:

    - All developers are part of the `DevTeam` IAM group, which includes shared permissions like CloudWatch read-only access and S3 read-only access.

- **Temporary Credentials and Assume Role**:

    - I Encouraged my team's developers to use temporary credentials by assuming roles with AWS CLI or SDK to minimize long-term credential exposure.

---

## C. Secrets Management

- **Used AWS Secrets Manager**:

    - We used Secrets Manager to store sensitive API keys or credentials securely.

- **How we Accessed Secrets Programmatically**:

    - We used SDKs (e.g., Python's boto3) to fetch secrets securely in application code.

---
