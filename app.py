from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import openai
import os
from collections import Counter
import re

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Data Storage
user_data = {}

# Comprehensive knowledge chunks from UK personal finance guide
knowledge_chunks = {
    "core_principles": """## Introduction & Overall Principles
1. Budget—pay important bills and existing debts.
2. Build a small emergency fund (1–3 months) if high-interest debt; more if no/low-interest debts.
3. Pension enrollment—ensure workplace scheme participation.
4. Assess debts—especially if >10% APR.
5. Build larger emergency fund (3–6 or 12 months).
6. Define goals—short-term (<5 years) vs. long-term (>5 years).
7. Short-term goals—cash or near-cash.
8. Long-term goals—pensions, Stocks & Shares ISA, overpaying mortgage.""",

    "budgeting": """## Budgeting & Essential Bills
1. Create budget—track monthly net income, essential outgoings, discretionary spending.
2. Pay necessary expenses—council tax, rent/mortgage, transport, utility bills.
3. Handling credit reliance:
   - Seek debt counseling if needed (StepChange, National Debtline)
   - Make minimum debt payments
   - Check benefit eligibility
4. Tools & Methods:
   - Envelope system: Physical/virtual category allocation
   - Zero-based budgeting: Every pound assigned
   - Software: YNAB, Money Dashboard, Emma
5. Regular Reviews:
   - Monthly bill checks
   - Annual review of utilities, subscriptions, insurance""",

    "emergency_fund": """## Emergency Fund
- Purpose: Covers unexpected costs (repairs, job loss, medical)
- Amount:
  - With expensive debt: 1 month's outgoings minimum
  - Debt-free: 3-6 months (up to 12 if job insecure)
- Access & Account Type:
  - Must be instantly accessible
  - Use easy-access savings or premium bonds
  - Avoid investing these funds—liquidity essential
- Management:
  - Keep separate from daily spending
  - Replenish after use
  - Consider smaller fund (1 month) if debt >10% APR""",

    "debt_management": """## Debt Management
1. Debt Categories:
   - Mortgage: Long-term, lower interest
   - Student Loans: Unique repayment terms
   - Credit Cards: 0% promotional or high-interest
   - Payday Loans: Extremely high interest, tackle ASAP

2. Priority Order:
   - Highest: Council tax/mortgage arrears (legal risks)
   - High-Interest Unsecured Debts (>10% APR)

3. Repayment Strategies:
   - Avalanche: Highest APR first (saves most interest)
   - Snowball: Smallest balance first (psychological wins)

4. Solutions:
   - Balance transfers: Check 0% deals and fees
   - Debt consolidation: Only if lower interest
   - Professional help: StepChange, National Debtline""",

    "pensions": """## Pensions & Retirement
1. Types:
   - Workplace: Auto-enrolment if earning >£10k/year
   - Private/SIPP: Self-chosen investments
   - State Pension: £203.85/week with 35 NI years

2. Key Points:
   - Contribute for maximum employer match
   - Annual allowance: £60k or annual salary
   - Tax relief: 20% basic rate, more for higher rates
   - Salary sacrifice saves on NI
   - Consider defined benefit transfers carefully

3. Retirement Planning:
   - Take 25% tax-free lump sum option
   - Plan for gap before state pension
   - Consider drawdown strategies""",

    "investments": """## Investments & ISAs
1. Basic Concepts:
   - Equities: Company ownership
   - Bonds: Government/corporate lending
   - Funds: Pooled investments
   - Risk/Return correlation

2. ISA Types:
   - Stocks & Shares: Tax-free investment growth
   - Cash ISA: Tax-free interest
   - Lifetime ISA: 25% bonus, home/retirement
   - £20k annual total limit

3. Strategy:
   - Global diversification
   - Asset allocation by age/risk tolerance
   - Consider passive vs active funds
   - Regular rebalancing""",

    "property": """## Property & Living Costs
1. Housing:
   - Rent vs Mortgage trade-offs
   - Council tax bands and discounts
   - Utility management and savings
   - Building vs contents insurance

2. BTL Considerations:
   - HMO regulations and yields
   - Company vs personal ownership
   - Tax implications and CGT
   - Landlord legal requirements

3. Costs:
   - Average groceries: £200-300/month/adult
   - Transport: Car vs public transit costs
   - Childcare: ~£50/day, check support schemes""",

    "insurance": """## Insurance & Protection
1. Essential Insurance:
   - Car insurance (legal requirement)
   - Buildings insurance (if homeowner)
   - Contents insurance
   - Life insurance (if dependents)

2. Additional Coverage:
   - Income protection
   - Critical illness cover
   - Private medical insurance
   - Family income benefit

3. Business Protection:
   - Key person insurance
   - Professional indemnity
   - Public liability""",

    "tax_planning": """## Tax & Legal
1. Income Tax Planning:
   - Personal allowance: £12,570
   - Tax bands and rates
   - National Insurance contributions
   - Salary sacrifice benefits

2. Advanced Planning:
   - High earner considerations
   - Capital gains tax management
   - Inheritance tax planning
   - Trust structures

3. Legal Considerations:
   - Wills and estate planning
   - Power of attorney
   - Joint accounts
   - Gifting rules""",
    
    "emergency_fund": """## Emergency Fund
- If you have high-interest debt, aim for 1–3 months of essential outgoings
- If debt-free, aim for 3–6 months (up to 12 months if job insecure)""",
    
    # ... [rest of the knowledge chunks remain the same]
}

def get_relevant_chunks(query, n=2):
    # Simple keyword matching
    query_words = set(re.findall(r'\w+', query.lower()))
    
    # Calculate relevance scores
    chunk_scores = {}
    for topic, content in knowledge_chunks.items():
        content_words = set(re.findall(r'\w+', content.lower()))
        score = len(query_words.intersection(content_words))
        chunk_scores[topic] = score
    
    # Get top n most relevant chunks
    relevant_topics = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:n]
    return [knowledge_chunks[topic] for topic, _ in relevant_topics]

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/details", methods=["GET"])
def details():
    return render_template("details.html")

@app.route("/chat", methods=["GET"])
def chat():
    return render_template("chat.html")

@app.route("/static/<path:filename>")
def custom_static(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

@app.route("/submit_details", methods=["POST"])
def submit_details():
    global user_data
    user_data = request.json
    return jsonify({"status": "success", "message": "Details submitted successfully!"})

@app.route("/ask_bot", methods=["POST"])
def ask_bot():
    global user_data
    data = request.json
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Get relevant knowledge chunks
        relevant_chunks = get_relevant_chunks(user_message)
        relevant_knowledge = "\n\n".join(relevant_chunks)

        prompt = f"""You are Doughbot, a UK financial assistant. Provide advice based on:

Financial Knowledge:
{relevant_knowledge}

User Details:
Age: {user_data.get('age')}
Income: {user_data.get('income')}
Savings: {user_data.get('savings')}
Investments: {user_data.get('investments')}
Debt: {user_data.get('debt')}

User Query: {user_message}"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Doughbot, a helpful UK financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)