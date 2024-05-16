
Designed to help customers

```markdown
# Automated AWS EFS Compliance Checker

This project provides an automated solution to ensure that your EC2 instances use the recommended "noresvport" mount option for AWS EFS (Elastic File System). The solution leverages AWS Lambda, AWS Config, and S3 to automate compliance checks and report results.

## Project Overview

- **Automated Compliance Checks**: Automatically checks EC2 instances for the "noresvport" mount option.
- **Simplified Operations**: Reduces the need for manual checks.
- **Detailed Reporting**: Provides compliance status in AWS Config and stores detailed results in an S3 bucket.

## Setup Instructions

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/your-username/efs-compliance-checker.git
    cd efs-compliance-checker
    ```

2. **Upload Lambda Function Code**:
    - Zip the `lambda_function.py` script.
    - Upload the zipped file to your S3 bucket.

3. **Deploy with CloudFormation**:
    - Navigate to the AWS CloudFormation console.
    - Create a new stack using the `efs-cloudformation-template.yaml`.
    - Provide the required parameters (S3 bucket names and paths).

4. **AWS Config Settings**:
    - Enable AWS Config with continuous recording for specific resource types:
      - AWS IAM Policy, User, Role, Group
      - AWS S3 Bucket
      - AWS EC2 Instance
      - AWS EFS FileSystem
      - AWS Lambda Function
      - AWS CloudFormation Stack

## Resources

- **CloudFormation Template**: `efs-cloudformation-template.yaml`
- **Lambda Function**: `lambda_function.py`

For full setup instructions and details, please refer to the [Medium article](https://medium.com/your-article-link).

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

---

**Note**: This project was built with the help of my reliable friend "Robert" alias ChatGPT. :D Using prompt engineering and collaborative effort, we were able to bring this project to life.

This is a personal project and not affiliated with AWS or Amazon. Contributions are welcome, but please validate the solution for your use case before deploying it in production.
```

This version of the `README.md` file is concise yet informative, providing an overview of the project, setup instructions, resources, and a link to the detailed Medium article for full instructions.
