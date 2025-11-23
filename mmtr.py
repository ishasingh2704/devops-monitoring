import subprocess
import requests
import time
import json

# --- CONFIG ---
DOCKER_IMAGE = "lalit1029/python-service:latest"
DEPLOYMENT = "python-service"
NAMESPACE = "default"
PROMETHEUS_URL = "http://prometheus-server.monitoring.svc.cluster.local:80"
CHAOS_MANIFEST = "python-chaos.yaml"

# --- STEP 1: Git Commit ---
def git_commit(message="Automated commit for MMTR"):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Git commit pushed")

# --- STEP 2: Deploy to Kubernetes ---
def deploy_new_image():
    subprocess.run([
        "kubectl", "set", "image", f"deployment/{DEPLOYMENT}",
        f"{DEPLOYMENT}={DOCKER_IMAGE}", "-n", NAMESPACE
    ], check=True)
    subprocess.run([
        "kubectl", "rollout", "status", f"deployment/{DEPLOYMENT}", "-n", NAMESPACE
    ], check=True)
    print("✅ Deployment updated")

# --- STEP 3: Chaos Experiment ---
def run_chaos_experiment():
    subprocess.run(["kubectl", "apply", "-f", CHAOS_MANIFEST], check=True)
    print("🔥 Chaos experiment started (pod kill)")
    time.sleep(40)  # wait for chaos duration
    subprocess.run(["kubectl", "delete", "-f", CHAOS_MANIFEST], check=True)
    print("✅ Chaos experiment finished")

# --- STEP 4: Validate Monitoring ---
def validate_monitoring():
    query = 'up{job="python-service", instance=~".*5000"}'
    resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    data = resp.json()
    results = data.get("data", {}).get("result", [])
    if results:
        print("📊 Prometheus UP metric:", json.dumps(results, indent=2))
        print("✅ Monitoring validated")
    else:
        print("❌ No UP metric found — check Prometheus scrape config")

# --- MAIN FLOW ---
if __name__ == "__main__":
    git_commit("MMTR pipeline run")
    deploy_new_image()
    run_chaos_experiment()
    validate_monitoring()
