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

      # Terraform passes the backend's Cloud Run URL to the frontend as an env var.
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