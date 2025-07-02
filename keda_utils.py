import subprocess
import os

def create_scaledobject():
    manifest_path = os.path.join("manifests", "scaledobject.yaml")
    scaledobject_name = "jupyter-scaler"

    if not os.path.exists(manifest_path):
        print(f"❌ Manifest file not found at {manifest_path}")
        return {"status": "error", "message": "Manifest file missing"}

    try:
        print(f"📦 Applying ScaledObject from: {manifest_path} ...")
        apply_proc = subprocess.run(
            ["kubectl", "apply", "-f", manifest_path, "-n", "keda"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print(f"✅ Applied:\n{apply_proc.stdout.decode().strip()}")

        print(f"🔍 Verifying ScaledObject `{scaledobject_name}` ...")
        get_proc = subprocess.run(
            ["kubectl", "get", "scaledobject", scaledobject_name, "-n", "keda"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print(f"✅ ScaledObject exists:\n{get_proc.stdout.decode().strip()}")

        return {"status": "success", "message": "ScaledObject applied and verified in keda namespace"}

    except subprocess.CalledProcessError as e:
        print(f"❌ Error:\n{e.stderr.decode().strip()}")
        return {"status": "error", "message": e.stderr.decode().strip()}
