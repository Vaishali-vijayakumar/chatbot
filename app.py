from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
user_data = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()
    
    if sender not in user_data:
        user_data[sender] = {'step': 0}

    step = user_data[sender]['step']

    if step == 0:
        msg.body("🙏 வணக்கம்! I’ll help you check eligibility for govt schemes. Shall we begin? (Yes/No)")
        user_data[sender]['step'] = 1

    elif step == 1:
        if 'yes' in incoming_msg.lower():
            msg.body("📌 Please tell me your age (in years):")
            user_data[sender]['step'] = 2
        else:
            msg.body("Okay. Type 'Hi' anytime to start again.")
            user_data[sender]['step'] = 0

    elif step == 2:
        try:
            user_data[sender]['age'] = int(incoming_msg)
            msg.body("💰 What is your monthly family income (in ₹)?")
            user_data[sender]['step'] = 3
        except ValueError:
            msg.body("❗ Please enter a valid number for age.")

    elif step == 3:
        user_data[sender]['income'] = int(incoming_msg.replace("₹", "").replace(",", "").strip())
        msg.body("🏷️ Caste? (SC/ST/OBC/General):")
        user_data[sender]['step'] = 4

    elif step == 4:
        user_data[sender]['caste'] = incoming_msg.upper()
        msg.body("📍 State and District? (e.g., Tamil Nadu, Thanjavur):")
        user_data[sender]['step'] = 5

    elif step == 5:
        user_data[sender]['location'] = incoming_msg
        msg.body("👩‍🌾 Occupation? (Farmer/Student/Widow/Unemployed/etc.):")
        user_data[sender]['step'] = 6

    elif step == 6:
        user_data[sender]['occupation'] = incoming_msg
        age = user_data[sender]['age']
        income = user_data[sender]['income']
        caste = user_data[sender]['caste']
        occ = user_data[sender]['occupation'].lower()
        state = user_data[sender]['location'].lower()

        response_text = "🎯 Based on your profile, you may be eligible for:\n"

        # Central Schemes
        if occ == 'farmer':
            response_text += "- 🌾 **PM-KISAN** (₹6000/year) [Small & Marginal Farmers]\n"
            response_text += "- 🏠 **PMAY Gramin** (Rural Housing Assistance)\n"

        if age >= 60:
            response_text += "- 👵 **Indira Gandhi National Old Age Pension Scheme** (₹1000/month)\n"

        if occ == 'widow':
            response_text += "- 👩‍🦳 **Widow Pension Scheme** (₹500–₹1000/month depending on state)\n"

        if occ == 'unemployed' and age <= 30:
            response_text += "- 🧑‍💻 **PMEGP** (Loan for Self-employment)\n"
            response_text += "- 📚 **National Career Service** (Job & skill training)\n"

        if caste in ['SC', 'ST']:
            response_text += "- 🏫 **Pre-Matric/Post-Matric Scholarships** for SC/ST\n"
            response_text += "- 🏠 **Dr. Ambedkar Housing Scheme**\n"

        if caste in ['OBC']:
            response_text += "- 📘 **OBC Scholarships** (Central/State-sponsored)\n"

        if income < 15000:
            response_text += "- 🏥 **Ayushman Bharat - PMJAY** (₹5 lakh insurance/year)\n"

        if occ == 'student' and age <= 25:
            response_text += "- 🎓 **National Means-cum-Merit Scholarship**\n"
            response_text += "- 💡 **State-level Free Education or Fee Waiver Schemes**\n"

        # State-specific logic
        if "tamil nadu" in state:
            response_text += "- 🧕 **Kalaignar Magalir Urimai Thogai** (₹1000/month for women heads)\n"
            response_text += "- 🎓 **Free Laptop Scheme for Students**\n"
        elif "uttar pradesh" in state:
            response_text += "- 👩‍🦳 **UP Widow Pension Scheme**\n"
            response_text += "- 📘 **UP Kanya Vidya Dhan Yojana**\n"
        elif "karnataka" in state:
            response_text += "- 👩‍🎓 **Yuva Nidhi** (₹3000 for unemployed graduates)\n"
            response_text += "- 📄 **OBC Certificate Assistance**\n"
        elif "bihar" in state:
            response_text += "- 👧 **Mukhyamantri Kanya Utthan Yojana** (₹50,000 for girls)\n"
            response_text += "- 🎓 **Bihar Student Credit Card Scheme**\n"

        response_text += "\n📋 Want application links or documents? Type: `Apply PM-KISAN` or `Apply Ayushman`"

        msg.body(response_text)
        user_data[sender]['step'] = 0  # Reset after match

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
