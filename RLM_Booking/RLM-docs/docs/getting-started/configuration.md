# Configuration

This guide details the configuration settings and environment variables required to run the project. Make sure these are set correctly to ensure smooth operation in both development and production environments.

---

## Environment Variables

The following environment variables should be added to the `.env` files for both the backend (Django) and frontend (React) applications.

### Backend (.env in root directory)

1. **DJANGO_SECRET_KEY**: Secret key for Django's cryptographic signing.
   - Example: `DJANGO_SECRET_KEY=your_secret_key`

2. **DATABASE_URL**: URL connection string for the database.
   - Example: `DATABASE_URL=postgres://username:password@localhost:5432/database_name`

3. **AWS_ACCESS_KEY_ID**: AWS access key for cloud services.
   - Example: `AWS_ACCESS_KEY_ID=your_aws_key`

4. **AWS_SECRET_ACCESS_KEY**: AWS secret access key for cloud services.
   - Example: `AWS_SECRET_ACCESS_KEY=your_aws_secret`

5. **OTHER_BACKEND_VARIABLES**: [For future env variables, with examples and explanations.]

---

### Frontend (.env in `frontend` directory)

1. **REACT_APP_API_URL**: URL for the backend API to connect to the Django server.
   - Example: `REACT_APP_API_URL=http://localhost:8000/api`

2. **OTHER_FRONTEND_VARIABLES**: [Future frontend-specific variables here, if applicable.]

---

## Configuration Files

In addition to environment variables, the project may use specific configuration files. Here are the key ones: (none right now)

---

### Django Settings

- **settings.py**: Modify settings for database connection, installed apps, middleware, and other configurations.
  - Ensure `ALLOWED_HOSTS` includes your development and production domains.
  - Set `DEBUG = True` for development and `DEBUG = False` for production.

---

### AWS CLI Configuration

To interact with AWS services, the AWS CLI must be configured with access credentials:

1. Run `aws configure` in the terminal and enter:
   - **Access Key ID**
   - **Secret Access Key**
   - **Default Region**

2. Check `~/.aws/credentials` if you need to review your AWS configuration.

---

### Docker Configuration (for Production)

Docker may be used in the future for production. Configuration files will be provided, and steps to build and run Docker containers will be updated here.

---

## Additional Notes

- **Storing Secrets Securely**: For production, avoid hardcoding secrets in code. Use a secure secret management service (e.g., AWS Secrets Manager) if available.
- **Configuration Updates**: Whenever a configuration change is made, update this document and any corresponding `.env` files to maintain accurate setup instructions.

---
