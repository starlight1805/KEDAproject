import os
import subprocess
import yaml
from jinja2 import Template

def run_cmd(cmd, check=True):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"Command failed: {cmd}\n{e.output.decode().strip()}")
        return None

def render_and_apply_yaml(template_path, parameters):
    """Render Jinja2 template and apply with kubectl"""
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
    print("🚀 Creating Jupyter notebook deployment using YAML template...")

    template_path = "manifests/jupyter_deployment.yaml"

    parameters = {
        "image": image,
        "port": port,
        "cpu_request": cpu_request,
        "memory_request": memory_request,
        "cpu_limit": cpu_limit,
        "memory_limit": memory_limit
    }

    render_and_apply_yaml(template_path, parameters)

    print("✅ Jupyter notebook deployment created.")
    
    # Gather service info
    print("🔍 Fetching service endpoint...")
    svc_output = run_cmd("kubectl get svc jupyter-service -n keda -o json")
    svc_info = yaml.safe_load(svc_output)
    
    node_port = svc_info["spec"]["ports"][0]["nodePort"]
    cluster_ip = svc_info["spec"].get("clusterIP", "N/A")

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

    print("✅ Deployment Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    return summary
