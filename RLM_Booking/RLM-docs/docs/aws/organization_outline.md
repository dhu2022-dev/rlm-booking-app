# AWS Setup and Organization for Client Project

This document covers my team's initial organizational structure outline to deploy AWS resources efficiently across development and production environments. Specifics on how each team member fits in this structure can be found in iam_permissions.md.

---

## AWS Systems Manager - Application Manager

- **Path**: AWS Management Console > Systems Manager > Application Manager.
- **Steps**:

    1. **Create New Application**: Name it based on the project (e.g., `ArtistRecommenderApp`). We named ours `RLM_Booking`.
    2. **Tagging**: Our tags were `Client: RLM`, `Project: Booking`, `Environment: Developer` and `Environment: Production` in the setup. The point is to organize the application, there's room to add more necessary tags later.

> **Purpose**: The Application Manager provides a high-level view of resources and configurations tied to this specific client project.

---

## Environment Separation

- **Development** and **Production** environments should be isolated to avoid data and configuration conflicts.

### Environment-Specific Resources

- Created separate resources per environment (e.g., different S3 buckets, Lambda functions, databases).
- Used tags like `Environment: Development` and `Environment: Production` to distinguish between them.

### Access Control

- Restricted Production access to specific team members.
- Development resources can have broader access for testing purposes.

---

## Use of AWS Organizations for Multi-Client Management

### Dedicated AWS Account

- **Purpose**: Keeps resources, billing, and permissions isolated.
- **Recommendation Outside this Project Scope**: **AWS Organizations** is used for managing multiple clients. This allows for consistent policies and centralized billing management. BAI Exec will have access to the AWS Organization that your AWS Account (not your personal, the client one) is managed by.

---
