from flask import Flask, Response, jsonify
from flask_cors import CORS
import threading
import json
import paramiko
import re
import queue

app = Flask(__name__)
CORS(app)  

data_queue = queue.Queue()

# def ssh_data_fetcher():
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
#     command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
#     stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

#     pattern = re.compile(r"(\{.*\})")
#     for line in stdout:
#         match = pattern.search(line)
#         if match:
#             try:
#                 data = eval(match.group()) 
#                 data_queue.put(data)
#             except:
#                 continue


# USAR EM CASO DE DEBUG


def ssh_data_fetcher():
    print("Iniciando conexão SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
    print("Conectado!")
    command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    pattern = re.compile(r"\{.*?\}")
    for line in stdout:
        print("RECEBIDO:", line)  # <--- debug
        match = pattern.search(line)
        if match:
            try:
                data = json.loads(match.group())
                data_queue.put(data)
            except Exception as e:
                print("Erro ao processar linha:", e)


# Eliminar antes do lançamento, pode ser um risco de segurança (so existe para meios de teste)
# No momento esta desativado

def shutdown():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
    command = "sudo /sbin/shutdown now"
    ssh.exec_command(command, get_pty=True)

@app.route("/shutdown", methods=["POST"])
def shutdown_pi():
    print("Shutdown request received!")  
    try:
        shutdown()
        return jsonify(status="success", message="Shutdown command sent."), 200
    except Exception as e:
        print("Erro ao desligar:", e)
        return jsonify(status="error", message=str(e)), 500
    
@app.route("/stream")
def stream():
    def event_stream():
        while True:
            data = data_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    threading.Thread(target=ssh_data_fetcher, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)