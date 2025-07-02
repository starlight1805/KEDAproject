import yaml

def create_scaledobject():
    print("⚙️ Creating KEDA ScaledObject...")
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
        keda = cfg["keda"]

    scaledobject = {
        "apiVersion": "keda.sh/v1alpha1",
        "kind": "ScaledObject",
        "metadata": {"name": "jupyter-kafka-scaler"},
        "spec": {
            "scaleTargetRef": {"name": cfg["deployment"]["name"]},
            "minReplicaCount": keda["minReplicaCount"],
            "maxReplicaCount": keda["maxReplicaCount"],
            "triggers": [{
                "type": "kafka",
                "metadata": {
                    "bootstrapServers": keda["broker"],
                    "topic": keda["topic"],
                    "consumerGroup": keda["consumerGroup"],
                    "lagThreshold": str(keda["lagThreshold"])
                }
            }]
        }
    }

    with open("scaledobject.yaml", "w") as f:
        yaml.dump(scaledobject, f)

    run("kubectl apply -f scaledobject.yaml")
    print("✅ ScaledObject created.")

def run(cmd):
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {cmd}\n{result.stderr}")
