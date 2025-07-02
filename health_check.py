import subprocess

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def check_deployment_health(name):
    """
    Check if a Kubernetes deployment has available replicas.
    Returns True if healthy, False otherwise.
    """
    print(f"{CYAN}Checking health of deployment: {name}{RESET}\n")

    # Build kubectl command to fetch available replicas
    cmd = f"kubectl get deployment {name} -n keda -o=jsonpath='{{.status.availableReplicas}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        available = result.stdout.strip().strip("'")

        if available and available.isdigit() and int(available) > 0:
            print(f"{GREEN}✔ Deployment '{name}' is healthy with {available} replica(s) available.{RESET}\n")
            return True
        else:
            print(f"{YELLOW}⚠ Deployment '{name}' is reachable but has no available replicas.{RESET}\n")
            return False
    else:
        print(f"{RED}✖ Failed to check health of deployment '{name}'. Error:\n{result.stderr.strip()}{RESET}\n")
        return False
