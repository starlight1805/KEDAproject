import subprocess
import yaml

def deploy_jupyter():
    print("📄 Deploying Jupyter Notebook...")
    run("kubectl apply -f jupyter_deployment.yaml")
    print("✅ Jupyter deployed.")

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {cmd}\n{result.stderr}")
    return result.stdout
