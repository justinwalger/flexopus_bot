terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

resource "google_artifact_registry_repository" "flexopus" {
  location      = "europe-west1"
  repository_id = "flexopus"
  format        = "DOCKER"
}

resource "google_service_account" "ci_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "CI/CD deployer for GitHub Actions"
}

resource "google_artifact_registry_repository_iam_member" "ci_deployer_writer" {
  location   = google_artifact_registry_repository.flexopus.location
  repository = google_artifact_registry_repository.flexopus.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.ci_deployer.email}"
}

resource "google_project_iam_member" "ci_deployer_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.ci_deployer.email}"
}

resource "google_project_iam_member" "ci_deployer_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.ci_deployer.email}"
}

resource "google_service_account_key" "ci_deployer_key" {
  service_account_id = google_service_account.ci_deployer.name
}

# fastapi backend
resource "google_cloud_run_v2_service" "fastapi_backend" {
  name     = "fastapi-backend"
  location = "europe-west1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.backend_image
      
      ports {
        container_port = 8080
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  project  = google_cloud_run_v2_service.fastapi_backend.project
  location = google_cloud_run_v2_service.fastapi_backend.location
  name     = google_cloud_run_v2_service.fastapi_backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service" "streamlit_frontend" {
  name     = "streamlit-frontend"
  location = "europe-west1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.frontend_image

      env {
        name  = "BACKEND_API_URL"
        value = "${google_cloud_run_v2_service.fastapi_backend.uri}/api"
      }

      ports {
        container_port = 8080
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  project  = google_cloud_run_v2_service.streamlit_frontend.project
  location = google_cloud_run_v2_service.streamlit_frontend.location
  name     = google_cloud_run_v2_service.streamlit_frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "frontend_url" {
  description = "public frontend url"
  value       = google_cloud_run_v2_service.streamlit_frontend.uri
}

output "ci_deployer_key" {
  EOT
  value       = google_service_account_key.ci_deployer_key.private_key
  sensitive   = true
}