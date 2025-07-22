## Project Overview
This project delivers an **automated, end-to-end AWS solution** built with **AWS CDK** (Infrastructure as Code) and deployed via a **manual GitHub Actions** workflow.

- Creates an **S3 bucket** and uploads sample files on every deploy  
- Deploys a **Python 3.9 Lambda** function that:
  - Lists every object in the bucket  
  - Publishes execution details to an SNS topic  
  - Returns `{"objects": [...]}` to the caller  
- Publishes execution details to an SNS topic with an e‑mail subscription  
- Uses a **least-privilege IAM role**, granting only S3 read and SNS publish permissions

---

## Repository Layout

```
.
├── infrastructure/          # CDK app (S3 bucket, SNS topic, IAM role, Lambda, file deploy)
├── lambda/
│   └── list_objects/        # Lambda handler (`index.py`)
├── sample_files/            # Two demo images uploaded to S3 on deploy
├── tests/                   # Manual invoke script & `event.json`
└── .github/
    └── workflows/           # GitHub Actions workflow (`basic_workflow_dispatch.yml`)
```

---

## Setup & Deployment

1. **Fork or clone** this repository.  
2. In your GitHub repo, go to **Settings → Secrets → Actions**, and add:
   - `AWS_ACCESS_KEY_ID`  
   - `AWS_SECRET_ACCESS_KEY`  
   - `AWS_REGION` (e.g. `us-east-1`)  
3. Navigate to **Actions → Manual CDK Deploy → Run workflow**.  
4. The workflow will:
   1. Check out the code  
   2. Configure AWS credentials  
   3. Install CDK CLI and Python dependencies  
   4. Run `cdk bootstrap` and `cdk deploy --all`  
5. Monitor the logs; on success, you will have an S3 bucket, SNS topic, and Lambda deployed.

---

## Manual Lambda Test Instructions

1. Ensure your local AWS CLI is configured:
   ```bash
   aws configure
   ```
2. From the repository root, run:

   **CMD**  
   ```cmd
   cd tests
   invoke_lambda.bat
   ```

   **PowerShell**  
   ```powershell
   cd tests
   .\invoke_lambda.ps1
   ```

3. The script will:
   - Invoke the Lambda with `tests/event.json` (empty payload)  
   - Print the JSON response to `output.json`  
   - Trigger an SNS e‑mail to your inbox with execution details  

---

## Tools & Frameworks Used

- **AWS CDK (v2, Python)** — Infrastructure as Code  
- **GitHub Actions** — CI/CD pipeline (manual deploy)  
- **AWS CLI** — Local/scripted Lambda invocation  
- **boto3** — AWS SDK inside the Lambda
