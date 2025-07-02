import subprocess

def check_deployment_health(name):
    print(f"🔍 Checking health of {name}...")
    cmd = f"kubectl get deployment {name} -o=jsonpath='{{.status.availableReplicas}}' -n keda"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip() != "":
        print(f"✅ {name} is healthy with {result.stdout.strip()} replicas running.")
    else:
        print(f"⚠️  Deployment {name} may not be healthy.")
