from flask import Flask, render_template, request, redirect
import mysql.connector
import random
import json
import matplotlib.pyplot as plt
import io
import base64
import requests
from typing import Dict, Any, List
import logging
import traceback
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host='77.37.35.12',
    user='u121769371_ki_aiml_test',
    password='Ki_kr_aiml@18!$#$',
    database='u121769371_ki_aiml_test'
)
cursor = db.cursor()
#gemini api like chatgpt to fetch info online
GEMINI_API_KEY = "AIzaSyD0KRTZb617Cfk5erBijoAOzPOf_RIiDyw"
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

GEMINI_API_KEY_2 = "AIzaSyAaAmnqRERlxE5GwR87ccr7RNzNiuvwi0o"
if GEMINI_API_KEY_2 is None:
    raise ValueError("GEMINI_API_KEY_2 environment variable is not set")

# Create the nirftop100 table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS nirftop100 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_name VARCHAR(255) UNIQUE,
    SS FLOAT,
    FSR FLOAT,
    FQE FLOAT,
    FRU FLOAT,
    OE FLOAT,
    MIR FLOAT,
    PU FLOAT,
    QP FLOAT,
    IPR FLOAT,
    FPPP FLOAT,
    SDG FLOAT,
    GUE FLOAT,
    GPHD FLOAT,
    RD FLOAT,
    WD FLOAT,
    ESCS FLOAT,
    PCS FLOAT,
    PR FLOAT,
    overall_score FLOAT,
    `Rank` INT
)
""")

# Check if the overall_score column exists
cursor.execute("SHOW COLUMNS FROM nirftop100 LIKE 'overall_score'")
overall_score_column_exists = cursor.fetchone() is not None

# Add the overall_score column to the nirftop100 table if it doesn't exist
if not overall_score_column_exists:
    cursor.execute("""
    ALTER TABLE nirftop100
    ADD COLUMN overall_score FLOAT
    """)
    db.commit()

# Check if the Rank column exists
cursor.execute("SHOW COLUMNS FROM nirftop100 LIKE 'Rank'")
rank_column_exists = cursor.fetchone() is not None

# Add the Rank column to the nirftop100 table if it doesn't exist
if not rank_column_exists:
    cursor.execute("""
    ALTER TABLE nirftop100
    ADD COLUMN `Rank` INT
    """)
    db.commit()

# List of college names
college_names = [
    "Indian Institute of Technology Madras",
    "Indian Institute of Science, Bengaluru",
    "Indian Institute of Technology Bombay",
    "Indian Institute of Technology Delhi",
    "Indian Institute of Technology Kanpur",
    "Indian Institute of Technology Kharagpur",
    "All India Institute of Medical Sciences Delhi",
    "Indian Institute of Technology Roorkee",
    "Indian Institute of Technology Guwahati",
    "Jawaharlal Nehru University",
    # Add more colleges as needed
]

# Generate data for each college in the list
def generate_college_data(college_name):
    return {
        "college_name": college_name,
        "SS": round(random.uniform(0, 20), 2),
        "FSR": round(random.uniform(0, 25), 2),
        "FQE": round(random.uniform(0, 20), 2),
        "FRU": round(random.uniform(0, 20), 2),
        "OE": round(random.uniform(0, 10), 2),
        "MIR": round(random.uniform(0, 5), 2),        
        "PU": round(random.uniform(0, 30), 2),
        "QP": round(random.uniform(0, 30), 2),
        "IPR": round(random.uniform(0, 15), 2),
        "FPPP": round(random.uniform(0, 15), 2),
        "SDG": round(random.uniform(0, 10), 2),
        "GUE": round(random.uniform(0, 60), 2),
        "GPHD": round(random.uniform(0, 40), 2),
        "RD": round(random.uniform(0, 30), 2),
        "WD": round(random.uniform(0, 30), 2),
        "ESCS": round(random.uniform(0, 20), 2),
        "PCS": round(random.uniform(0, 20), 2),
        "PR": round(random.uniform(0, 20), 2),
    }

# Insert data into the database
colleges = []
for college_name in college_names:
    data = generate_college_data(college_name)
    SS, FSR, FQE, FRU, OE, MIR = data["SS"], data["FSR"], data["FQE"], data["FRU"], data["OE"], data["MIR"]    
    PU,QP,IPR,FPPP,SDG=data["PU"],data["QP"],data["IPR"],data["FPPP"],data["SDG"]
    GUE, GPHD = data["GUE"], data["GPHD"]
    RD, WD, ESCS, PCS = data["RD"], data["WD"], data["ESCS"], data["PCS"]
    PR=data["PR"]

    TLR = (SS + FSR + FQE + FRU + OE + MIR) * 0.30
    RP = (PU + QP + IPR + FPPP + SDG ) * 0.30
    GO = (GUE + GPHD) * 0.20
    OI = (RD + WD + ESCS + PCS) * 0.10
    PR =(PR)*0.10

    overall_score = TLR + RP + GO + OI + PR
    overall_score = min(overall_score, 100)

    colleges.append((
        data["college_name"], data["SS"], data["FSR"], data["FQE"], data["FRU"],
        data["OE"], data["MIR"],data["PU"],data["QP"],data["IPR"],data["FPPP"],data["SDG"],data["GUE"], data["GPHD"], data["RD"],
        data["WD"], data["ESCS"], data["PCS"],data["PR"], overall_score
    ))

insert_query = """
INSERT INTO nirftop100 (college_name, SS, FSR, FQE, FRU, OE, MIR,PU,QP,IPR,FPPP,SDG, GUE, GPHD, RD, WD, ESCS, PCS,PR, overall_score)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    SS=VALUES(SS), FSR=VALUES(FSR), FQE=VALUES(FQE), FRU=VALUES(FRU),
    OE=VALUES(OE), MIR=VALUES(MIR), PU=VALUES(PU),QP=VALUES(QP),IPR=VALUES(IPR),FPPP=VALUES(FPPP),SDG=VALUES(SDG),GUE=VALUES(GUE), GPHD=VALUES(GPHD),
    RD=VALUES(RD), WD=VALUES(WD), ESCS=VALUES(ESCS), PCS=VALUES(PCS),PR=VALUES(PR),
    overall_score=VALUES(overall_score)
"""
cursor.executemany(insert_query, colleges)
db.commit()

#print(f"{cursor.rowcount} colleges data inserted or updated successfully.")

def calculate_total_overall_score(data):
    SS, FSR, FQE, FRU, OE, MIR = data["SS"], data["FSR"], data["FQE"], data["FRU"], data["OE"], data["MIR"]    
    PU,QP,IPR,FPPP,SDG=data["PU"],data["QP"],data["IPR"],data["FPPP"],data["SDG"]
    GUE, GPHD = data["GUE"], data["GPHD"]
    RD, WD, ESCS, PCS = data["RD"], data["WD"], data["ESCS"], data["PCS"]
    PR=data["PR"]

    TLR = (SS + FSR + FQE + FRU + OE + MIR) * 0.30
    RP = (PU + QP + IPR + FPPP + SDG ) * 0.30
    GO = (GUE + GPHD) * 0.20
    OI = (RD + WD + ESCS + PCS) * 0.10
    PR =(PR)*0.10

    total_overall_score = TLR + RP + GO + OI + PR
    total_overall_score = min(overall_score, 100)

    return total_overall_score

# Insert data into the database
colleges = []
for college_name in college_names:
    data = generate_college_data(college_name)
    overall_score = calculate_total_overall_score(data)
    total_overall_score = overall_score  # Since it's the same for this example

    colleges.append((
        data["college_name"], data["SS"], data["FSR"], data["FQE"], data["FRU"],
        data["OE"], data["MIR"],data["PU"],data["QP"],data["IPR"],data["FPPP"],data["SDG"],data["GUE"], data["GPHD"], data["RD"],
        data["WD"], data["ESCS"], data["PCS"],data["PR"], overall_score, total_overall_score
    ))

insert_query = """
INSERT INTO nirftop100 (college_name, SS, FSR, FQE, FRU, OE, MIR,PU,QP,IPR,FPPP,SDG, GUE, GPHD, RD, WD, ESCS, PCS,PR,overall_score, total_overall_score)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
SS=VALUES(SS), FSR=VALUES(FSR), FQE=VALUES(FQE), FRU=VALUES(FRU),
OE=VALUES(OE), MIR=VALUES(MIR), PU=VALUES(PU),QP=VALUES(QP),IPR=VALUES(IPR),FPPP=VALUES(FPPP),SDG=VALUES(SDG), GUE=VALUES(GUE), GPHD=VALUES(GPHD),
RD=VALUES(RD), WD=VALUES(WD), ESCS=VALUES(ESCS), PCS=VALUES(PCS),PR=VALUES(PR),
overall_score=VALUES(overall_score), total_overall_score=VALUES(total_overall_score)
"""
cursor.executemany(insert_query, colleges)
db.commit()

# Populate the Rank column with the provided data
rank_data = [
    ("Indian Institute of Technology Madras", 1),
    ("Indian Institute of Science, Bengaluru", 2),
    ("Indian Institute of Technology Bombay", 3),
    ("Indian Institute of Technology Delhi", 4),
    ("Indian Institute of Technology Kanpur", 5),
    ("Indian Institute of Technology Kharagpur", 6),
    ("All India Institute of Medical Sciences Delhi", 7),
    ("Indian Institute of Technology Roorkee", 8),
    ("Indian Institute of Technology Guwahati", 9),
    ("Jawaharlal Nehru University", 10),
    # Add more rank data as needed
]

update_query = """
UPDATE nirftop100
SET `Rank` = %s
WHERE college_name = %s
"""
cursor.executemany(update_query, [(rank, college) for college, rank in rank_data])
db.commit()

print(f"Rank data updated successfully")

# Home page (register a college)
@app.route('/')
def register():
    return render_template('register.html')
# this route is for register.html
@app.route('/register_college', methods=['POST'])
def register_college():
    college_name = request.form['college_name']
    data = {param: float(request.form[param]) for param in ["SS", "FSR", "FQE", "FRU", "OE", "MIR","PU","QP","IPR","FPPP","SDG", "GUE", "GPHD", "RD", "WD", "ESCS", "PCS","PR"]}

    # Calculate the overall score based on the formula
    SS, FSR, FQE, FRU, OE, MIR = data["SS"], data["FSR"], data["FQE"], data["FRU"], data["OE"], data["MIR"]    
    PU,QP,IPR,FPPP,SDG=data["PU"],data["QP"],data["IPR"],data["FPPP"],data["SDG"]
    GUE, GPHD = data["GUE"], data["GPHD"]
    RD, WD, ESCS, PCS = data["RD"], data["WD"], data["ESCS"], data["PCS"]
    PR=data["PR"]

    TLR = (SS + FSR + FQE + FRU + OE + MIR) * 0.30
    RP = (PU + QP + IPR + FPPP + SDG ) * 0.30
    GO = (GUE + GPHD) * 0.20
    OI = (RD + WD + ESCS + PCS) * 0.10
    PR =(PR)*0.10

    overall_score = TLR + RP + GO + OI + PR
    overall_score = min(overall_score, 60)

    # Insert data into the database
    cursor.execute(f"""
        INSERT INTO nirftop100 (college_name, SS, FSR, FQE, FRU, OE, MIR,PU,QP,IPR,FPPP,SDG, GUE, GPHD, RD, WD, ESCS, PCS,PR, overall_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        SS=VALUES(SS), FSR=VALUES(FSR), FQE=VALUES(FQE), FRU=VALUES(FRU),OE=VALUES(OE), MIR=VALUES(MIR),
        PU=VALUES(PU),QP=VALUES(QP),IPR=VALUES(IPR),FPPP=VALUES(FPPP),SDG=VALUES(SDG), 
        GUE=VALUES(GUE), GPHD=VALUES(GPHD),
        RD=VALUES(RD), WD=VALUES(WD), ESCS=VALUES(ESCS), PCS=VALUES(PCS),
        PR=VALUES(PR),
        overall_score=VALUES(overall_score)
    """, [college_name] + list(data.values()) + [overall_score])
    db.commit()
    return redirect('/insights')

@app.route("/comparison")
def comparison():
    cursor.execute("SELECT DISTINCT college_name FROM nirftop100")
    registered_colleges = [row[0] for row in cursor.fetchall()]
    return render_template("comparison.html", colleges=registered_colleges)

@app.route("/compare_colleges", methods=["POST"])
def compare_colleges():
    selected_colleges = request.form.getlist("selected_colleges")
    comparison_category = request.form["comparison_category"]

    if not selected_colleges:
        return "Please select at least one college for comparison.", 400

    rank_conditions = {
        "top_10": "`Rank` BETWEEN 1 AND 10",
        "top_11_50": "`Rank` BETWEEN 11 AND 50",
        "top_51_100": "`Rank` BETWEEN 51 AND 100",
    }

    if comparison_category not in rank_conditions:
        return "Invalid comparison category.", 400

    try:
        # Fetch NIRF data
        cursor.execute(f"SELECT * FROM nirftop100 WHERE {rank_conditions[comparison_category]}")
        nirf_data = cursor.fetchall()

        # Fetch user-registered data
        placeholders = ", ".join(["%s"] * len(selected_colleges))
        cursor.execute(f"SELECT * FROM nirftop100 WHERE college_name IN ({placeholders})", selected_colleges)
        registered_data = cursor.fetchall()

        # Filter out rows where the overall score is None or "N/A"
        nirf_data = [row for row in nirf_data if row[-2] is not None and row[-2] != "N/A"]
        registered_data = [row for row in registered_data if row[-2] is not None and row[-2] != "N/A"]

        # If all rows are filtered out, return a message
        if not nirf_data:
            return "No valid NIRF data found for the selected comparison category.", 400
        if not registered_data:
            return "No valid registered college data found.", 400

        nirf_data_json = json.dumps(nirf_data, default=str)
        registered_data_json = json.dumps(registered_data, default=str)

        # Generate insights and visualization graph
        insights = generate_insights(nirf_data_json, registered_data_json)
        image_url = generate_visualization_graph(nirf_data, registered_data)

        # Return results to template
        return render_template(
            "result.html",
            nirf_data=json.loads(nirf_data_json),
            registered_data=json.loads(registered_data_json),
            insights=insights,
            image_url=image_url,
        )
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

def generate_insights(nirf_data_json, registered_data_json):
    try:
        contents = [{"parts": [{"text": f"NIRF Data: {nirf_data_json}\nRegistered Data: {registered_data_json} ### Overall Score Calculation\n"
    "**Formula**:\n"
    "1. **TLR Component**: (SS + FSR + FQE + FRU + OE + MIR) x 0.30\n"
    "2. **GO Component**: (GUE + GPHD) x 0.20\n"
    "3. **OI Component**: (RD + WD + ESCS + PCS) x 0.10\n\n"
    "**Final Score**: Sum of the above three components, capped at 60.\n\n"
    "### Ranking Thresholds\n"
    "- 45-60: Top 1-10 rankings\n"
    "- 35-45: Top 15-30 rankings\n"
    "- 25-30: Top 40-60 rankings\n"
    "- 15-20: Top 80-100 rankings\n"
    "- Below 15: Ranked 100-150\n "}]}]
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": contents},
        )

        if response.status_code == 200:
            return response.json().get("candidates", [{}])[0].get("content", {})
        return {"error": f"Failed to generate insights. Error: {response.text}"}
    except Exception as e:
        return {"error": f"An error occurred while generating insights: {str(e)}"}

def generate_visualization_graph(nirf_data, registered_data):
    try:
        # Extract data for NIRF colleges
        nirf_colleges = [college[1] for college in nirf_data]
        nirf_scores = [college[-2] if college[-2] is not None else 0 for college in nirf_data]

        # Extract data for registered colleges
        registered_colleges = [college[1] for college in registered_data]
        registered_scores = [college[-2] if college[-2] is not None else 0 for college in registered_data]

        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.bar(nirf_colleges, nirf_scores, color="blue", label="NIRF Data", alpha=0.7)
        plt.bar(registered_colleges, registered_scores, color="orange", label="Registered Data", alpha=0.7)

        plt.xlabel("College Names")
        plt.ylabel("Overall Scores")
        plt.title("Comparison of NIRF and Registered College Data")
        plt.xticks(rotation=45, ha="right")
        plt.legend()

        # Save the plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        # Encode the image to base64
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        return f"An error occurred while generating visualization: {str(e)}"

GEMINI_API_KEYS = {
    "rank": "AIzaSyD0KRTZb617Cfk5erBijoAOzPOf_RIiDyw",
    "suggestion": "AIzaSyAaAmnqRERlxE5GwR87ccr7RNzNiuvwi0o"
}

# Parameter Descriptions
PARAMETER_DESCRIPTIONS = {
    "SS": "Student Strength",
    "FSR": "Faculty-Student Ratio",
    "FQE": "Faculty Qualification and Experience",
    "FRU": "Financial Resources Utilization",
    "OE": "Overall Enrollment",
    "MIR": "Merit Intake Ratio",
    "PU":"Combined Metric for Publications",
    "QP":"Combined Metric for Quality of Publications",
    "IPR":"IPR and Patents: Published and Granted",
    "FPPP":"Footprint of Projects, Professional Practice and Executive Development Programs",
    "SDG":"Combined Metric for Publication and Citation in SDGs",
    "GUE": "Graduate Employment",
    "GPHD": "Graduating PhD",
    "RD": "Research and Development",
    "WD": "Women Diversity",
    "ESCS": "Economically and Socially Challenged Students",
    "PCS": "Physically Challenged Students",
    "PR":"Peer Perception: Employers & Academic Peer"
}

# Add the total_overall_score column to the nirftop100 table if it doesn't exist
cursor.execute("SHOW COLUMNS FROM nirftop100 LIKE 'total_overall_score'")
total_overall_score_column_exists = cursor.fetchone() is not None

if not total_overall_score_column_exists:
    cursor.execute("""
    ALTER TABLE nirftop100
    ADD COLUMN total_overall_score FLOAT
    """)
    db.commit()
# function for gemini api 
def call_gemini_api(content: str, key: str) -> dict:
    """
    Call Gemini API for content generation based on the provided content and API key.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": content}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Gemini API response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        return None
# this route is for insights.html page 
@app.route('/insights', methods=['GET', 'POST'])
def insights():
    if request.method == 'POST':
        try:
            college_name = request.form.get("college_name")

            if not college_name:
                return render_template("insights.html",
                                    error="No college name provided",
                                    insights_data=None)

            cursor.execute("SELECT SS, FSR, FQE, FRU, OE, MIR,PU,QP,IPR,FPPP,SDG,GUE, GPHD, RD, WD, ESCS, PCS,PR FROM nirftop100 WHERE college_name = %s", (college_name,))
            college_data = cursor.fetchone()

            if not college_data:
                return render_template("insights.html",
                                    error="College data not found",
                                    insights_data=None)

            insights_data = {}
            parameters = list(PARAMETER_DESCRIPTIONS.keys())

            # Process individual parameters
            for i, param in enumerate(parameters):
                value = college_data[i]
                if value is not None:
                    try:
                        param_value = float(value)
                        insights_data[param] = {
                            "Response": f"{param_value:.2f}",
                            "In Between Rank": "",
                            "Suggestion": ""
                        }
                    except (ValueError, TypeError) as e:
                        insights_data[param] = {
                            "Response": "Error",
                            "In Between Rank": "Unable to calculate",
                            "Suggestion": "Invalid value"
                        }

            # Calculate Total Score
            try:
                tlr_component = sum(float(insights_data[param]['Response']) for param in ['SS', 'FSR', 'FQE', 'FRU', 'OE', 'MIR']) * 0.30
                rp_component = sum(float(insights_data[param]['Response']) for param in ['PU', 'QP', 'IPR', 'FPPP', 'SDG']) * 0.30
                go_component = sum(float(insights_data[param]['Response']) for param in ['GUE', 'GPHD']) * 0.20
                oi_component = sum(float(insights_data[param]['Response']) for param in ['RD', 'WD', 'ESCS', 'PCS']) * 0.10
                pr_component = sum(float(insights_data[param]['Response']) for param in ['PR']) * 0.10

                total_score = min(tlr_component + rp_component + go_component + oi_component + pr_component, 100)

                # Add Total to insights_data
                insights_data['Total'] = {
                    "Response": f"{total_score:.2f}",
                    "In Between Rank": "",
                    "Suggestion": ""
                }

            except Exception as e:
                logger.error(f"Error calculating total score: {str(e)}")
                insights_data['Total'] = {
                    "Response": "Error",
                    "In Between Rank": "Unable to calculate",
                    "Suggestion": "Error calculating total score"
                }

            # Process rankings and suggestions for all parameters including Total
            # context string can be customized for ranking so that we can get the desired rankings 
            for param, details in insights_data.items():
                context = (
                    "Act as an expert in NIRF Rank Prediction.\n\n"
                    "Based on the provided data, confidently predict the ranking range for the parameter {parameter} with a value of {value}.\n\n"
                    "Provide a confident and specific ranking range in one line answer. Do not include any additional text or explanations.\n\n"
                    "NIRF COMPREHENSIVE RANK PREDICTION FRAMEWORK\n"
"DOMAIN WEIGHTS:\n"
"1. Teaching, Learning & Resources (TLR): 0.30 (30 marks)\n"
"2. Research & Professional Practice (RP): 0.30 (30 marks)\n"
"3. Graduation Outcomes (GO): 0.20 (20 marks)\n"
"4. Outreach & Inclusivity (OI): 0.10 (10 marks)\n"
"5. Perception (PR): 0.10 (10 marks)\n"
"\n"
"I. TEACHING, LEARNING & RESOURCES (TLR)\n"
"\n"
"A. Student Strength (SS)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"B. Faculty-Student Ratio (FSR)\n"
"- 15-25 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"C. Faculty Qualification & Experience (FQE)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"D. Financial Resources Utilization (FRU)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"E. Online Education (OE)\n"
"- 8-10 marks: Top 1-10 rankings\n"
"- 5-7 marks: Top 15-30 rankings\n"
"- Less than 4 marks: Top 40-60 rankings\n"
"- 0-2 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"II. RESEARCH & PROFESSIONAL PRACTICE (RP)\n"
"\n"
"A. Publications (PU)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"B. Quality of Publications (QP)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"C. IPR and Patents (IPR)\n"
"- 13-15 marks: Top 1-10 rankings\n"
"- 10-12 marks: Top 15-30 rankings\n"
"- 7-11 marks: Top 40-60 rankings\n"
"- 1-7 marks: Top 80-100 rankings\n"
"- Below 1 mark: Ranked 100-150\n"
"\n"
"III. GRADUATION OUTCOMES (GO)\n"
"\n"
"A. University Examinations (GUE)\n"
"- 50-60 marks: Top 1-10 rankings\n"
"- 40-45 marks: Top 15-30 rankings\n"
"- Less than 30 marks: Top 40-60 rankings\n"
"- 20 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"B. PhD Students Graduated (GPHD)\n"
"- 50-60 marks: Top 1-10 rankings\n"
"- 40-45 marks: Top 15-30 rankings\n"
"- Less than 30 marks: Top 40-60 rankings\n"
"- 20 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"IV. OUTREACH & INCLUSIVITY (OI)\n"
"\n"
"A. Regional Diversity (RD)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"B. Women Diversity (WD)\n"
"- 20-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"V. PERCEPTION (PR)\n"
"- 80-100 marks: Top 1-10 rankings\n"
"- 60-80 marks: Top 15-30 rankings\n"
"- 40-60 marks: Top 40-60 rankings\n"
"- 20-40 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"FINAL SCORE CALCULATION:\n"
"Total Score = (TLR × 0.30) + (RP × 0.30) + (GO × 0.20) + (OI × 0.10) + (PR × 0.10)\n"
"\n"
"OVERALL RANKING THRESHOLDS:\n"
"- 68-100 marks: Top 1-10 rankings\n"
"- 67-55 marks: Top 11-40 rankings\n"
"- 54-51 marks: Top 40-80 rankings\n"
"- 49-44 marks: Top 80-100 rankings\n"
"- Below 43 marks: Ranked 100-150\n"
"\n"
"PREDICTION INSTRUCTIONS:\n"
"1. Input specific marks for each parameter\n"
"2. Match input to corresponding ranking range\n"
"3. Calculate weighted domain scores\n"
"4. Determine final institutional ranking\n"
                ).format(
                    parameter="Overall Score" if param == "Total" else PARAMETER_DESCRIPTIONS[param],
                    value=details['Response']
                )
# context_suggestion can be customized for ranking so that we can get the desired rankings
                context_suggestion = (
                    "Act as an expert in NIRF National Institutional Ranking Framework.\n\n"
                    "How to improve {parameter} with a value of {value}? also try to give feedback like  if you want  imporve this {parameter} score to the maximum score or top ranking like the rang \n\n"
                    "Provide detailed suggestions and strategies for improvement  \n\n"
                    "NIRF COMPREHENSIVE RANK PREDICTION FRAMEWORK\n"
"DOMAIN WEIGHTS:\n"
"1. Teaching, Learning & Resources (TLR): 0.30 (30 marks)\n"
"2. Research & Professional Practice (RP): 0.30 (30 marks)\n"
"3. Graduation Outcomes (GO): 0.20 (20 marks)\n"
"4. Outreach & Inclusivity (OI): 0.10 (10 marks)\n"
"5. Perception (PR): 0.10 (10 marks)\n"
"\n"
"I. TEACHING, LEARNING & RESOURCES (TLR)\n"
"\n"
"A. Student Strength (SS)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"B. Faculty-Student Ratio (FSR)\n"
"- 15-25 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"C. Faculty Qualification & Experience (FQE)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"D. Financial Resources Utilization (FRU)\n"
"- 15-20 marks: Top 1-10 rankings\n"
"- 10-15 marks: Top 15-30 rankings\n"
"- Less than 10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"E. Online Education (OE)\n"
"- 8-10 marks: Top 1-10 rankings\n"
"- 5-7 marks: Top 15-30 rankings\n"
"- Less than 4 marks: Top 40-60 rankings\n"
"- 0-2 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"II. RESEARCH & PROFESSIONAL PRACTICE (RP)\n"
"\n"
"A. Publications (PU)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"B. Quality of Publications (QP)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"C. IPR and Patents (IPR)\n"
"- 13-15 marks: Top 1-10 rankings\n"
"- 10-12 marks: Top 15-30 rankings\n"
"- 7-11 marks: Top 40-60 rankings\n"
"- 1-7 marks: Top 80-100 rankings\n"
"- Below 1 mark: Ranked 100-150\n"
"\n"
"III. GRADUATION OUTCOMES (GO)\n"
"\n"
"A. University Examinations (GUE)\n"
"- 50-60 marks: Top 1-10 rankings\n"
"- 40-45 marks: Top 15-30 rankings\n"
"- Less than 30 marks: Top 40-60 rankings\n"
"- 20 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"B. PhD Students Graduated (GPHD)\n"
"- 50-60 marks: Top 1-10 rankings\n"
"- 40-45 marks: Top 15-30 rankings\n"
"- Less than 30 marks: Top 40-60 rankings\n"
"- 20 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"IV. OUTREACH & INCLUSIVITY (OI)\n"
"\n"
"A. Regional Diversity (RD)\n"
"- 19-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 3-13 marks: Top 80-100 rankings\n"
"- Below 3 marks: Ranked 100-150\n"
"\n"
"B. Women Diversity (WD)\n"
"- 20-30 marks: Top 1-10 rankings\n"
"- 15-20 marks: Top 15-30 rankings\n"
"- 5-10 marks: Top 40-60 rankings\n"
"- 0-5 marks: Top 80-100 rankings\n"
"- Below 0 marks: Ranked 100-150\n"
"\n"
"V. PERCEPTION (PR)\n"
"- 80-100 marks: Top 1-10 rankings\n"
"- 60-80 marks: Top 15-30 rankings\n"
"- 40-60 marks: Top 40-60 rankings\n"
"- 20-40 marks: Top 80-100 rankings\n"
"- Below 20 marks: Ranked 100-150\n"
"\n"
"FINAL SCORE CALCULATION:\n"
"Total Score = (TLR × 0.30) + (RP × 0.30) + (GO × 0.20) + (OI × 0.10) + (PR × 0.10)\n"
"\n"
"OVERALL RANKING THRESHOLDS:\n"
"- 68-100 marks: Top 1-10 rankings\n"
"- 67-55 marks: Top 11-40 rankings\n"
"- 54-51 marks: Top 40-80 rankings\n"
"- 49-44 marks: Top 80-100 rankings\n"
"- Below 43 marks: Ranked 100-150\n"
"\n"
"PREDICTION INSTRUCTIONS:\n"
"1. Input specific marks for each parameter\n"
"2. Match input to corresponding ranking range\n"
"3. Calculate weighted domain scores\n"
"4. Determine final institutional ranking\n"
                ).format(
                    parameter="Overall Score" if param == "Total" else PARAMETER_DESCRIPTIONS[param],
                    value=details['Response']
                )
# debugging code 
                gemini_response_rank = call_gemini_api(context, GEMINI_API_KEYS["rank"])
                if gemini_response_rank:
                    rank_text = gemini_response_rank.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response from Gemini API for rank')
                    rank_lines = rank_text.split('\n')
                    insights_data[param]['In Between Rank'] = '\n'.join(rank_lines[:2])
                else:
                    insights_data[param]['In Between Rank'] = 'Error calling Gemini API for rank'

                gemini_response_suggestion = call_gemini_api(context_suggestion, GEMINI_API_KEYS["suggestion"])
                if gemini_response_suggestion:
                    suggestion_text = gemini_response_suggestion.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response from Gemini API for suggestions')
                    formatted_suggestion = "\n".join([f"- {line}" for line in suggestion_text.split('\n')])
                    insights_data[param]['Suggestion'] = formatted_suggestion
                else:
                    insights_data[param]['Suggestion'] = 'Error calling Gemini API for suggestions'

            if not insights_data:
                return render_template("insights.html",
                                    error="Could not process the data format",
                                    insights_data=None)

            return render_template("insights.html",
                                insights_data=insights_data,
                                parameter_descriptions=PARAMETER_DESCRIPTIONS)

        except Exception as e:
            logger.error("Error in insights route:")
            logger.error(traceback.format_exc())
            return render_template("insights.html",
                                error=f"An error occurred: {str(e)}",
                                insights_data=None)

    return render_template("insights.html", insights_data=None)

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
