import subprocess
import sys
import platform
import os
import time

def start_services():
    os_type = platform.system().lower()
    print(f"Starting VAPT Scanner on {os_type}")

    # Start PostgreSQL (assuming it's installed)
    if os_type == "linux":
        subprocess.run(["sudo", "service", "postgresql", "start"])
    elif os_type == "windows":
        subprocess.run(["net", "start", "postgresql"])

    # Start backend
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd="./backend"
    )

    # Start frontend
    if os_type == "windows":
        frontend_process = subprocess.Popen(["npm.cmd", "start"], cwd="./frontend")
    else:
        frontend_process = subprocess.Popen(["npm", "start"], cwd="./frontend")

    print("Services started successfully!")
    print("Access the application at: http://localhost:3000")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    start_services()
