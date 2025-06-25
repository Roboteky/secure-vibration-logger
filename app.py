from flask import Flask, jsonify, render_template_string
from flask_httpauth import HTTPBasicAuth
from cryptography.fernet import Fernet
from datetime import datetime
import os
from collections import defaultdict

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {"admin": "pass123"}

@auth.get_password
def get_pw(username):
    return users.get(username)

@app.route("/data")
@auth.login_required
def view_data():
    try:
        with open("secret.key", "rb") as f:
            key = f.read()
        fernet = Fernet(key)

        with open("data/data.enc", "rb") as f:
            lines = f.readlines()

        raw_logs = []
        count_by_minute = defaultdict(int)

        for line in lines:
            try:
                msg = fernet.decrypt(line.strip()).decode()
                raw_logs.append(msg)

                if msg.startswith("["):
                    time_str = msg.split("]")[0][1:]
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    key_str = dt.strftime("%Y-%m-%d %H:%M")
                    count_by_minute[key_str] += 1
            except:
                raw_logs.append("[DECRYPTION ERROR]")

        chart_labels = list(count_by_minute.keys())
        chart_data = [count_by_minute[k] for k in chart_labels]

        html = """
        <html>
        <head>
            <title>Secure Vibration Logs</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h2>Secure Vibration Logs</h2>

            <canvas id="vibrationChart" width="800" height="300"></canvas>
            <script>
            const ctx = document.getElementById('vibrationChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: {{ labels|safe }},
                    datasets: [{
                        label: 'Vibration Events per Minute',
                        data: {{ data|safe }},
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        x: { title: { display: true, text: 'Time (minute)' } },
                        y: { title: { display: true, text: 'Vibration Events' }, beginAtZero: true }
                    }
                }
            });
            </script>

            <h3>Log Table</h3>
            <table border="1">
                <tr><th>#</th><th>Log Entry</th></tr>
                {% for i, entry in enumerate(data) %}
                <tr><td>{{ i+1 }}</td><td>{{ entry }}</td></tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, data=raw_logs, labels=chart_labels, data=chart_data)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')
