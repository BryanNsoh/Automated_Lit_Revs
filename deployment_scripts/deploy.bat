   @echo on
   setlocal enabledelayedexpansion

   echo Starting deployment process...

   REM Navigate to the project directory
   cd /d "C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Projects\Automated_Lit_Revs"
   echo Current directory: %CD%

   REM Set the project ID to apt-rite-378417
   gcloud config set project apt-rite-378417
   echo Project set to apt-rite-378417

   REM Enable all required Google Cloud APIs
   echo Enabling required Google Cloud APIs...
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

   REM Create an Artifact Registry repository (skip if it already exists)
   echo Creating/Checking Artifact Registry repository...
   gcloud artifacts repositories create lit-review-repo --repository-format=docker --location=us-central1 --description="Lit Review Agent Repo" || echo "Artifact Registry already exists, skipping..."

   REM Grant necessary permissions to the Compute Engine service account
   echo Granting necessary permissions...
   gcloud projects add-iam-policy-binding apt-rite-378417 ^
     --member="serviceAccount:127476142400-compute@developer.gserviceaccount.com" ^
     --role="roles/storage.objectViewer" ^
     --role="roles/logging.logWriter" ^
     --role="roles/artifactregistry.writer" ^
     --role="roles/secretmanager.secretAccessor" ^
     --role="roles/storage.admin"

   REM Build the Docker image using Cloud Build
   echo Building Docker image using Cloud Build...
   gcloud builds submit --tag us-central1-docker.pkg.dev/apt-rite-378417/lit-review-repo/literature-review-agent

   REM Deploy the Cloud Run service with environment variables and secret keys
   echo Deploying to Cloud Run...
   gcloud run deploy literature-review-agent --image us-central1-docker.pkg.dev/apt-rite-378417/lit-review-repo/literature-review-agent --platform managed --allow-unauthenticated --region=us-central1 --memory=1024Mi --set-env-vars CLOUD_LOGGING_ENABLED=true --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,CORE_API_KEY=CORE_API_KEY:latest"

   REM Grant public access to the Cloud Run service (all users)
   echo Granting public access...
   gcloud run deploy literature-review-agent --image us-central1-docker.pkg.dev/apt-rite-378417/lit-review-repo/literature-review-agent --platform managed --allow-unauthenticated --region=us-central1 --memory=1024Mi --set-env-vars CLOUD_LOGGING_ENABLED=true --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,CORE_API_KEY=CORE_API_KEY:latest" --ingress=all 

   REM Retrieve and display the Cloud Run service URL
   echo Retrieving service URL...
   for /f "tokens=*" %%a in ('gcloud run services describe literature-review-agent --region=us-central1 --format="value(status.url)"') do set SERVICE_URL=%%a

   echo Deployment complete. Your service is now publicly accessible.
   echo Service URL: %SERVICE_URL%
   pause