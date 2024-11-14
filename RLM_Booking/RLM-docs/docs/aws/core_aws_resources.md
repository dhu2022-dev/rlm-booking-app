# Core AWS Resources

This section details the core AWS resources my team set up and how for the client project, covering storage, processing, and machine learning components. It covers the high level design choices we made, why, and our basic configuration to get an idea of our general direction. 

---

## A. Data Storage and Management

### Amazon DynamoDB

- **Purpose**: Fast, scalable storage for structured data.
- **Relation to Project**:

    - Includes tables such as `Artists`, `Venues`, `Events`.
    - Configured **Read/Write Capacity** as needed. DynamoDB will scale automatically.

### Amazon S3

- **Purpose**: Stores unstructured data (e.g., images, reports).
- **Relation to Project**:

    - Includes buckets like `rlm-prod-artist-data`, `rlm-dev-event-reports`.
    - Enabled **versioning** for data tracking.

---

## B. Data Processing and Machine Learning

### AWS SageMaker

- **Purpose**: For training recommendation models and deploying them.
- **Relation to Project**:

    - Deployed a **Notebook Instance** for data exploration and model training.
    - Deployed trained models as endpoints for real-time recommendations.

### AWS Glue (ETL)

- **Purpose**: Data preparation tasks (e.g., cleaning data from external sources).
- **Relation to Project**:

    - Went to **Glue** in the AWS Console.
    - Created **Jobs** and **Crawlers** to extract, transform, and load data into DynamoDB or S3.

---

## C. API and Serverless Compute

### AWS Lambda

- **Purpose**: Serverless backend processes for handling real-time requests.
- **Relation to Project**:

    - Created functions for specific tasks (e.g., `RecommendArtist`, `FetchEventAnalytics`).
    - Connected Lambda functions to DynamoDB or SageMaker endpoints as needed.

### API Gateway

- **Purpose**: Creates RESTful APIs for frontend or external integration.
- **Relation to Project**:

    - Created an API and define endpoints (e.g., `/recommend`, `/analyze`, `/fetch-trends`).

---

## D. Monitoring and Logging

### Amazon CloudWatch

- **Purpose**: To monitor application metrics, setting alarms, and creating logs for AWS resources we used like Lambda and SageMaker.
- **Relation to Project**:

    - *Alarms*:

        - Create CloudWatch Alarms for critical metrics (e.g., Lambda function errors, SageMaker model performance).
        - Configure alarms to notify via Amazon SNS for immediate response.

    - *Logs*:

        - Enable logs for each Lambda function to track runtime data and troubleshoot errors.
        - For model monitoring, set up logs in SageMaker to track model performance over time.

---

### QuickSight

- **Purpose**: QuickSight can be used for visualizing analytics and historical data, creating BI dashboards if reporting is required.

- **Relation to Project**

    - *Data Sources*:

        - Connect QuickSight to S3, DynamoDB, or RDS as needed.

    - *Create Dashboards*:

        - Develop dashboards for key metrics (e.g., ticket sales, event performance, artist popularity).
        - Use visualizations to gain insights into data trends.

---
