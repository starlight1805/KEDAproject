import subprocess
import os
import time
import shutil

def run_cmd(cmd, check=True):
    """Run a shell command and return output."""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"❌ Command failed: {cmd}\n{e.output.decode().strip()}")
        return None

def check_kube_connection():
    """Check if connected to a Kubernetes cluster."""
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
        return check_kube_connection()

def install_helm():
    """Install Helm if not already installed."""
    print("📦 Checking Helm installation...")
    if shutil.which("helm"):
        version = run_cmd("helm version --short")
        print(f"✅ Helm is already installed: {version}")
    else:
        print("⏬ Installing Helm (you may need sudo)...")
        run_cmd("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
        version = run_cmd("helm version --short")
        print(f"✅ Helm installed: {version}")

def install_keda():
    """Install KEDA via Helm and verify the operator pod is running."""
    print("🚀 Installing KEDA via Helm...")
    run_cmd("helm repo add kedacore https://kedacore.github.io/charts")
    run_cmd("helm repo update")
    run_cmd("helm upgrade --install keda kedacore/keda --namespace keda --create-namespace")
    
    print("⏳ Waiting for KEDA operator pod to be Running...")
    for _ in range(30):
        output = run_cmd("kubectl get pods -n keda -l app=keda-operator -o jsonpath='{.items[0].status.phase}'", check=False)
        if output and output.strip("'") == "Running":
            print("✅ KEDA operator is running.\n")
            return
        time.sleep(2)
    raise RuntimeError("❌ KEDA operator failed to start or is stuck.")

def verify_tools():
    """Verify installations and summarize cluster status."""
    print("\n📋 Verifying tools and cluster status...")

    # Kubernetes Context
    print("\n🔧 Current Kubernetes context:")
    context = run_cmd("kubectl config current-context")
    print(f"📍 Context: {context}")

    # Nodes
    print("\n🖥️ Cluster Nodes:")
    nodes = run_cmd("kubectl get nodes -o wide")
    print(nodes)

    # Helm Releases
    print("\n📦 Helm Releases:")
    releases = run_cmd("helm list -A", check=False)
    print(releases if releases else "⚠️ No Helm releases found.")

    # KEDA Check
    print("\n📡 KEDA Status:")
    keda_pods = run_cmd("kubectl get pods -n keda", check=False)
    if "keda-operator" in keda_pods:
        print("✅ KEDA is installed and its pods are:\n" + keda_pods)
    else:
        print("❌ KEDA pods not found in 'keda' namespace.")

def connect_to_cluster():
    """High-level function to verify cluster and install Helm + KEDA."""
    check_kube_connection()
    install_helm()
    install_keda()
    verify_tools()
