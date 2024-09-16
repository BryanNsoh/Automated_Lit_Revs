@echo off
setlocal enabledelayedexpansion

REM Navigate to the project directory
cd /d "C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Projects\Automated_Lit_Revs"

REM Authenticate with Google Cloud
gcloud auth login

REM Load environment variables from .env file
for /f "tokens=1,2 delims==" %%G in (.env) do set %%G=%%H

REM Set the project ID to apt-rite-378417
gcloud config set project apt-rite-378417

REM Enable all required Google Cloud APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

REM Create an Artifact Registry repository (skip if it already exists)
gcloud artifacts repositories create lit-review-repo --repository-format=docker --location=us-central1 --description="Lit Review Agent Repo" || echo "Artifact Registry already exists, skipping..."

REM Grant necessary permissions to the Compute Engine service account
gcloud projects add-iam-policy-binding apt-rite-378417 ^
  --member="serviceAccount:127476142400-compute@developer.gserviceaccount.com" ^
  --role="roles/storage.objectViewer" ^
  --role="roles/logging.logWriter" ^
  --role="roles/artifactregistry.writer" ^
  --role="roles/secretmanager.secretAccessor" ^
  --role="roles/storage.admin"

REM Set up secrets by reading values from the environment variables
for %%K in (OPENAI_API_KEY CLAUDE_API_KEY COHERE_API_KEY TOGETHER_API_KEY SCOPUS_API_KEY CORE_API_KEY BREVO_API_KEY) do (
    echo Creating secret for %%K
    gcloud secrets create %%K --replication-policy="automatic" || echo Secret %%K already exists, updating...
    echo !%%K! | gcloud secrets versions add %%K --data-file=-
)

echo All secrets have been created or updated in Google Cloud Secret Manager.

REM Build and submit the Docker image to the Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/apt-rite-378417/lit-review-repo/literature-review-agent

REM Deploy the Cloud Run service with environment variables and secret keys
gcloud run deploy literature-review-agent ^
  --image us-central1-docker.pkg.dev/apt-rite-378417/lit-review-repo/literature-review-agent ^
  --platform managed ^
  --allow-unauthenticated ^
  --region=us-central1 ^
  --memory=1024Mi ^
  --set-env-vars CLOUD_LOGGING_ENABLED=true ^
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,CLAUDE_API_KEY=CLAUDE_API_KEY:latest,COHERE_API_KEY=COHERE_API_KEY:latest,TOGETHER_API_KEY=TOGETHER_API_KEY:latest,SCOPUS_API_KEY=SCOPUS_API_KEY:latest,CORE_API_KEY=CORE_API_KEY:latest,BREVO_API_KEY=BREVO_API_KEY:latest"

REM Grant public access to the Cloud Run service (all users)
gcloud run services add-iam-policy-binding literature-review-agent ^
  --region=us-central1 ^
  --member="allUsers" ^
  --role="roles/run.invoker"

REM Retrieve and display the Cloud Run service URL
for /f "tokens=*" %%a in ('gcloud run services describe literature-review-agent --region=us-central1 --format="value(status.url)"') do set SERVICE_URL=%%a

echo Deployment complete. Your service is now publicly accessible.
echo Service URL: %SERVICE_URL%
pause
