🏏 CrickEye – AI Cricket Coach 🚀Welcome to CrickEye – an AI-powered cricket coaching dashboard that lets you analyze player performance, generate smart alerts, and visualize team stats in real time!
Whether you're a hobbyist, coach, or developer, CrickEye makes performance analysis fun and intuitive.

🛠 Setup Instructions
1)💻 Clone the repository:
git clone <your-repo-url>

2)📂 Move into project folder:
cd CRICK_EYE

3)🛎 Create a virtual environment:
Windows:
python -m venv venv
venv\Scripts\activate

4)📦 Install dependencies:
pip install -r Backend/requirements.txt

5)🏃‍♂ Launch the Flask app: 
cd Backend
python app.py

6)🌐 Open the dashboard:
Visit http://127.0.0.1:5000 in your browser.

7)🔗 API Endpoints:
POST: 🚀 Add player performance to CSV storage
GET : 🏆 Fetch all player performance history

8)📊 Performance Analysis & Alert Logic
Batting:Strike rate > 150 ⚡ → “High Strike Rate” 🚩
Bowling:Economy rate < 6 🍀 → “Good Bowling” 🟢

Whenever these thresholds are reached:
🔔 Instant alerts are created
🚨 Alerts appear directly on dashboard
