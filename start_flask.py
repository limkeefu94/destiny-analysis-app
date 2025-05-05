import subprocess
import time

def start_flask():
    subprocess.Popen(["python", "da7_simulated_ai_analysis.py"])

if __name__ == "__main__":
    print("启动 Flask 服务中...")
    start_flask()
    time.sleep(3)  # 等待 Flask 启动
    print("Flask 服务已启动，端口 5000")