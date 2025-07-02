from cluster_utils import connect_to_cluster, install_helm, install_keda
from deploy_utils import create_jupyter_deployment
from keda_utils import create_scaledobject
from health_check import check_deployment_health

if __name__ == "__main__":
    print("🔧 Step 1: Connect to Kubernetes cluster")
    if not connect_to_cluster():
        print("🛑 Aborting: Cluster connection/setup failed.")
        exit(1)

    print("📦 Step 2: Deploy Jupyter Notebook")
    if not create_jupyter_deployment():
        print("🛑 Aborting: Jupyter deployment failed.")
        exit(1)

    print("⚙️ Step 3: Create KEDA ScaledObject")
    if not create_scaledobject():
        print("⚠️ Skipping health check: Failed to create ScaledObject.")
        exit(1)

    print("🩺 Step 4: Run Health Check")
    check_deployment_health("jupyter-notebook")
