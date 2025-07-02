import subprocess
import os
import time

def run_cmd(cmd, check=True):
    """Run a shell command and return output."""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"Command failed: {cmd}\n{e.output.decode().strip()}")
        return None


def check_kube_connection():
    """Check if the current kube context is connected to the cluster."""
    print("🔍 Verifying Kubernetes cluster connectivity...")
    try:
        output = run_cmd("kubectl cluster-info", check=False)
        if "Kubernetes control plane" in output or "is running" in output:
            print("✅ Connected to Kubernetes cluster.\n")
            return True
        else:
            raise Exception
    except Exception:
        print("❌ Not connected to any Kubernetes cluster.")
        kubeconfig = input("🔑 Please provide the path to your kubeconfig file (default: ~/.kube/config): ").strip() or os.path.expanduser("~/.kube/config")
        os.environ["KUBECONFIG"] = kubeconfig
        print(f"📂 Set KUBECONFIG to {kubeconfig}")
        return check_kube_connection()  # Try again recursively


def install_helm():
    """Install Helm if not already installed."""
    print("📦 Checking Helm installation...")
    try:
        version = run_cmd("helm version --short")
        print(f"✅ Helm is already installed: {version}")
    except Exception:
        print("⏬ Installing Helm (you may need sudo)...")
        run_cmd("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
        version = run_cmd("helm version --short")
        print(f"✅ Helm installed: {version}")


def install_keda():
    """Install KEDA using Helm and verify its status."""
    print("🚀 Installing KEDA via Helm...")
    run_cmd("helm repo add kedacore https://kedacore.github.io/charts")
    run_cmd("helm repo update")
    run_cmd("helm upgrade --install keda kedacore/keda --namespace keda --create-namespace")
    print("⏳ Waiting for KEDA operator pod to be Running...")

    for _ in range(30):
        try:
            output = run_cmd("kubectl get pods -n keda -l app=keda-operator -o jsonpath='{.items[0].status.phase}'", check=False)
            if output.strip("'") == "Running":
                print("✅ KEDA operator is running.\n")
                return
        except Exception:
            pass
        time.sleep(2)

    raise RuntimeError("❌ KEDA operator failed to start.")


def connect_to_cluster():
    """High-level function to verify cluster and install tooling."""
    check_kube_connection()
    install_helm()
    install_keda()

