# Installation Guide

This guide provides step-by-step instructions to set up the project for local development.

---

## Prerequisites

Ensure you have the following installed on your machine:

- **Python** (version 3.12)
- **Node.js** (version X.X) and **npm**
- **AWS CLI** (for cloud services interaction)
- **Docker** ([will populate in the future when we do production])

## Step 1: Clone the Repository

Clone the project repository from GitHub:

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

## Step 2: Set Up Backend (Django)

1. **Create a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2. **Install Dependencies**:

    Install the required Python packages listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**:

    Create a `.env` file in the root directory with the following variables:

    ```env
    DJANGO_SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    AWS_ACCESS_KEY_ID=your_aws_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret
    ```

    See configuration documentation for specific examples and additional info on this.

4. **Apply Migrations**:

    Set up the database by running migrations:

    ```bash
    python manage.py migrate
    ```

5. **Run the Development Server**:

    Start the Django server:

    ```bash
    python manage.py runserver
    ```

## Step 3: Set up Frontend (React)

1. **Navigate to the Frontend Directory**:

    ```bash
    cd frontend
    ```

2. **Install Dependencies**:

    Use npm to install the necessary packages:

    ```bash
    npm install
    ```

3. **Configure Environment Variables**:

    Create a *.env* file in the *frontend* directory with any frontend-specific environment variables:

    ```bash
    REACT_API_API_URL=http://localhost:8000/api
    ```

4. **Run the Development Server**:

    Start the React development server:

    ```bash
    npm start
    ```

## Step 4: Set up Cloud Services (AWS)

To connect to AWS resources:

1. **Configure AWS CLI**: Set up AWS credentials:

    ```bash
    aws configure
    ```

    Enter your AWS Access Key ID, Secret Access Key, and default region.

2. **Verify S3 and DynamoDB Access**:

    Ensure you have the correct permissions for S3 and DynamoDB. Contact <who.is.david101@gmail.com> for AWS Permissions if you are a developer for Red Light.

## Step 5: Running the Application

With both Django backend and React frontend running, you can access the application at:

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000>

---

## Troubleshooting

- **Common Issues**:
  - [Put stuff people struggle with here]
