import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Starting Streamlit Frontend Chat UI...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
