import subprocess
import os
import time
import shutil

# ANSI color codes for colored terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def run_cmd(cmd, check=True):
    """
    Run a shell command and return its decoded output.
    If check=True and the command fails, raise an error.
    """
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"{RED}Command failed: {cmd}\n{e.output.decode().strip()}{RESET}")
        return None

def check_kube_connection():
    """
    Check if the system is connected to a Kubernetes cluster.
    If not, prompt the user for a kubeconfig path and retry.
    """
    print(f"{CYAN}Verifying Kubernetes cluster connectivity...{RESET}")
    try:
        output = run_cmd("kubectl cluster-info", check=False)
        if "Kubernetes control plane" in output or "is running" in output:
            print(f"{GREEN}Connected to Kubernetes cluster.{RESET}\n")
            return True
        else:
            raise Exception
    except Exception:
        print(f"{RED}Not connected to any Kubernetes cluster.{RESET}")
        
        # Prompt user for kubeconfig path (default to ~/.kube/config)
        kubeconfig = input("Please provide the path to your kubeconfig file (default: ~/.kube/config): ").strip() or os.path.expanduser("~/.kube/config")
        os.environ["KUBECONFIG"] = kubeconfig
        
        print(f"Set KUBECONFIG to {kubeconfig}\n")
        
        # Retry after setting KUBECONFIG
        return check_kube_connection()

def install_helm():
    """
    Check if Helm is installed. If not, install it.
    Returns True on success, False on failure.
    """
    print(f"{CYAN}Checking Helm installation...{RESET}")
    try:
        if shutil.which("helm"):
            version = run_cmd("helm version --short")
            print(f"{GREEN}Helm is already installed: {version}{RESET}\n")
        else:
            print("Installing Helm (you may need sudo)...")
            run_cmd("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
            version = run_cmd("helm version --short")
            print(f"{GREEN}Helm installed: {version}{RESET}\n")
        return True
    except Exception as e:
        print(f"{RED}Helm installation failed: {e}{RESET}\n")
        return False

def install_keda():
    """
    Install KEDA using Helm and wait for the operator pod to be running.
    Returns True if successful, False otherwise.
    """
    print(f"{CYAN}Installing KEDA via Helm...{RESET}")
    try:
        # Add and update the KEDA Helm repo
        run_cmd("helm repo add kedacore https://kedacore.github.io/charts")
        run_cmd("helm repo update")

        # Install or upgrade the KEDA release with Cert Manager enabled
        run_cmd("helm upgrade --install keda kedacore/keda --namespace keda --create-namespace --set admissionWebhooks.certManager.enabled=true")

        print("Waiting for KEDA operator pod to be Running...\n")

        # Poll the pod status for a fixed number of attempts
        for _ in range(150):
            output = run_cmd("kubectl get pods -n keda -l app=keda-operator -o jsonpath='{.items[0].status.phase}'", check=False)
            if output and output.strip("'") == "Running":
                print(f"{GREEN}KEDA operator is running.{RESET}\n")
                return True
            time.sleep(2)

        raise RuntimeError("KEDA operator pod did not reach Running state in time.")
    except Exception as e:
        print(f"{RED}Failed to install or verify KEDA: {e}{RESET}\n")
        return False

def verify_tools():
    """
    Display cluster context, node info, Helm releases, and KEDA status.
    Used for verification after installation.
    """
    print(f"{CYAN}Verifying tools and cluster status...{RESET}\n")

    try:
        # Print current Kubernetes context
        print("Current Kubernetes context:")
        context = run_cmd("kubectl config current-context")
        print(f"  Context: {context}\n")

        # List all nodes with extended info
        print("Cluster Nodes:")
        nodes = run_cmd("kubectl get nodes -o wide")
        print(nodes + "\n")

        # List Helm releases in all namespaces
        print("Helm Releases:")
        releases = run_cmd("helm list -A", check=False)
        print(releases + "\n" if releases else f"{YELLOW}No Helm releases found.{RESET}\n")

        # Check if KEDA operator pod is running
        print("KEDA Status:")
        keda_pods = run_cmd("kubectl get pods -n keda", check=False)
        if keda_pods and "keda-operator" in keda_pods:
            print(f"{GREEN}KEDA is installed and its pods are:\n{RESET}{keda_pods}\n")
        else:
            print(f"{RED}KEDA pods not found in 'keda' namespace.{RESET}\n")
    except Exception as e:
        print(f"{RED}Failed to verify tools: {e}{RESET}\n")

def connect_to_cluster():
    """
    Top-level function that performs:
      1. Cluster connectivity check
      2. Helm installation
      3. KEDA installation
      4. Final verification
    
    Returns True only if all steps succeed.
    """
    print(f"{CYAN}\n========== Starting Cluster Setup =========={RESET}\n")

    if not check_kube_connection():
        print(f"{RED}Aborting: Kubernetes cluster not reachable.{RESET}\n")
        return False

    if not install_helm():
        print(f"{RED}Aborting: Helm installation failed.{RESET}\n")
        return False

    if not install_keda():
        print(f"{RED}Aborting: KEDA installation failed.{RESET}\n")
        return False

    # Only called if all previous steps succeeded
    verify_tools()
    return True
