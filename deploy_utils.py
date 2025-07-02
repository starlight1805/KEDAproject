import os
import subprocess
import yaml
from jinja2 import Template

# ANSI color codes for CLI
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def run_cmd(cmd, check=True):
    """Run a shell command and return its output."""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"{RED}Command failed: {cmd}\n{e.output.decode().strip()}{RESET}")
        return None

def render_and_apply_yaml(template_path, parameters):
    """Render a Jinja2 YAML template and apply it using kubectl."""
    with open(template_path) as f:
        template = Template(f.read())

    rendered_yaml = template.render(parameters)

    tmp_file = "/tmp/rendered_jupyter.yaml"
    with open(tmp_file, "w") as f:
        f.write(rendered_yaml)

    run_cmd(f"kubectl apply -f {tmp_file}")
    os.remove(tmp_file)

def create_jupyter_deployment(
    image="jupyter/base-notebook:latest",
    port=8888,
    cpu_request="100m",
    memory_request="128Mi",
    cpu_limit="500m",
    memory_limit="512Mi"
):
    """
    Deploy a Jupyter notebook using a templated Kubernetes YAML manifest.
    Returns True on success, False on failure.
    """
    print(f"{CYAN}Creating Jupyter notebook deployment...{RESET}\n")

    try:
        # Path to the Jinja2 YAML template
        template_path = "manifests/jupyter_deployment.yaml"

        # Template parameters for substitution
        parameters = {
            "image": image,
            "port": port,
            "cpu_request": cpu_request,
            "memory_request": memory_request,
            "cpu_limit": cpu_limit,
            "memory_limit": memory_limit
        }

        # Render and apply the deployment
        render_and_apply_yaml(template_path, parameters)

        print(f"{GREEN}Deployment created successfully.{RESET}\n")

        # Fetch service details
        print(f"{CYAN}Fetching service endpoint...{RESET}")
        svc_output = run_cmd("kubectl get svc jupyter-service -n keda -o json")
        svc_info = yaml.safe_load(svc_output)

        node_port = svc_info["spec"]["ports"][0]["nodePort"]
        cluster_ip = svc_info["spec"].get("clusterIP", "N/A")

        # Construct a summary details
        summary = {
            "deployment": "jupyter-notebook",
            "service": "jupyter-service",
            "port": port,
            "nodePort": node_port,
            "clusterIP": cluster_ip,
            "image": image,
            "resources": {
                "requests": {
                    "cpu": cpu_request,
                    "memory": memory_request
                },
                "limits": {
                    "cpu": cpu_limit,
                    "memory": memory_limit
                }
            }
        }

        print(f"\n{GREEN}Deployment Summary:{RESET}")
        for k, v in summary.items():
            print(f"  {k}: {v}")

        print()
        return True

    except Exception as e:
        print(f"{RED}Failed to create Jupyter deployment: {e}{RESET}\n")
        return False
