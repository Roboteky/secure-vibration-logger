from flask import Flask, jsonify, render_template_string, redirect
from flask_httpauth import HTTPBasicAuth
from cryptography.fernet import Fernet
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {"admin": "pass123"}

@auth.get_password
def get_pw(username):
    return users.get(username)

@app.route("/")
def index():
    return redirect("/data")

@app.route("/data")
@auth.login_required
def view_data():
    try:
        # Load encryption key
        with open("secret.key", "rb") as f:
            key = f.read()
        fernet = Fernet(key)

        # Read encrypted log file
        log_file_path = "data/data.enc"
        if not os.path.exists(log_file_path):
            return "<h3>No log file found. Please run the logger first.</h3>"

        with open(log_file_path, "rb") as f:
            lines = f.readlines()

        raw_logs = []
        count_by_minute = defaultdict(int)

        for line in lines:
            try:
                msg = fernet.decrypt(line.strip()).decode()
                raw_logs.append(msg)

                # Extract timestamp
                if msg.startswith("["):
                    time_str = msg.split("]")[0][1:]
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    minute_str = dt.strftime("%Y-%m-%d %H:%M")
                    count_by_minute[minute_str] += 1
            except Exception as e:
                raw_logs.append(f"[DECRYPTION ERROR] {str(e)}")

        chart_labels = list(count_by_minute.keys())
        chart_data = [count_by_minute[k] for k in chart_labels]

        # Debug output
        print("Chart Labels:", chart_labels)
        print("Chart Data:", chart_data)

        html = """
        <html>
        <head>
            <title>Secure Vibration Logs</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h2>Secure Vibration Logs</h2>

            {% if chart_data %}
              <canvas id="vibrationChart" width="800" height="300"></canvas>
              <script>
              const ctx = document.getElementById('vibrationChart').getContext('2d');
              const chart = new Chart(ctx, {
                  type: 'bar',
                  data: {
                      labels: {{ labels|safe }},
                      datasets: [{
                          label: 'Vibration Events per Minute',
                          data: {{ chart_data|safe }},
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
            {% else %}
              <p>No vibration events to display yet.</p>
            {% endif %}

            <h3>Log Table</h3>
            <table border="1">
                <tr><th>#</th><th>Log Entry</th></tr>
                {% for entry in logs %}
                  <tr><td>{{ loop.index }}</td><td>{{ entry }}</td></tr>
                {% endfor %}
            </table>
        </body>
        </html>cc
        """
        return render_template_string(html, logs=raw_logs, labels=chart_labels, chart_data=chart_data)

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')
