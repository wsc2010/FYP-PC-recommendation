# Mr. Wong Shi Chin
# /index.py
# Main flask app
# 16/7/2022
# 20/7/2022
from locale import currency
from flask import Flask, request, jsonify, render_template, url_for
import os
from google.cloud import dialogflow
from threading import Thread

from algorithm.pc_recommendation import generate_recommendation
from algorithm.utils import update_build_naming

app = Flask(__name__)


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    if text:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        print("=" * 20)
        print("Query text: {}".format(response.query_result.query_text))
        print(
            "Detected intent: {} (confidence: {})\n".format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence,
            )
        )
        print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
        
        return response.query_result.fulfillment_text


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/build_pc', methods=['POST', 'GET'])
def build_pc():
    if request.method == 'POST':
        userBudget = int(request.form['budget'])
        userUseCase = request.form.getlist('gridRadios')[0]
        print(userBudget)
        print(userUseCase)

        sel_build = generate_recommendation(userBudget, userUseCase, 250, 25, 0.25, top3 = True)
        if sel_build:
            first, second, third = sel_build
            update_build_naming(first)
            update_build_naming(second)
            update_build_naming(third)
            return render_template('output.html', build1 = first, build2 = second, build3 = third)
        else:
            return render_template('form.html', insufficient_budget = True)
        

@app.route('/output', methods=['POST', 'GET'])
def output():
    return render_template('output.html')
    
# POST request from Dialogflow webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    intent = data['queryResult']['intent']['displayName']

    if intent == 'Recommend PC - yes':
        budget = data['queryResult']['outputContexts'][0]['parameters']['budget']['amount']
        currency = data['queryResult']['outputContexts'][0]['parameters']['budget']['currency']
        use_case = data['queryResult']['outputContexts'][0]['parameters']['use_case']
        print(budget)
        print(use_case)
        if currency != "USD":
            reply = {
            "fulfillmentText": "Sorry, budget only works in USD only",
            }
            return jsonify(reply)

        if budget < 1200:
            reply = {
            "fulfillmentText": "Unfortunately, that is not enough for a recommendation. Minimum is 1200 USD.",
            }
            return jsonify(reply)

        sel_build = generate_recommendation(budget, use_case, 50, 15, 0.25)
        update_build_naming(sel_build)

        output = (f"<p><strong>CPU</strong>: {sel_build.sel_cpu.name}</p><p><strong>Motherboard</strong>: {sel_build.sel_mobo.name}</p>\
                <p><strong>GPU</strong>: {sel_build.sel_gpu.full_name}</p><p><strong>RAM</strong>: {sel_build.sel_mem.full_name}</p>\
                    <p><strong>Storage</strong>: {sel_build.sel_storage.full_name}</p><p><strong>Cooler</strong>: {sel_build.sel_cooler.name}</p>\
                        <p><strong>PSU</strong>: {sel_build.sel_psu.full_name}</p><p><strong>Case</strong>: {sel_build.sel_case.name}</p>\
                            <p><strong>Total Cost: </strong>: {sel_build.totalCost():.2f}$</p>\
                            <p>!This is not likely the best possible build due to the limited time for a response. Use the manual form to get better builds!</p>")
        reply = {
            "fulfillmentText": output,
            }
        return jsonify(reply)

    elif intent == 'randomizer':
        sel_build = generate_recommendation(get_random=True)
        update_build_naming(sel_build)

        output = (f"<p>Here is a randomly generated build.</p>\
            <p><strong>CPU</strong>: {sel_build.sel_cpu.name}</p><p><strong>Motherboard</strong>: {sel_build.sel_mobo.name}</p>\
                <p><strong>GPU</strong>: {sel_build.sel_gpu.full_name}</p><p><strong>RAM</strong>: {sel_build.sel_mem.full_name}</p>\
                    <p><strong>Storage</strong>: {sel_build.sel_storage.full_name}</p><p><strong>Cooler</strong>: {sel_build.sel_cooler.name}</p>\
                        <p><strong>PSU</strong>: {sel_build.sel_psu.full_name}</p><p><strong>Case</strong>: {sel_build.sel_case.name}</p>\
                            <p><strong>Total Cost: </strong>: {sel_build.totalCost():.2f}$</p>")

        reply = {
            "fulfillmentText": output,
        }
        return jsonify(reply)


@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "123456789", message, 'en')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)

# run Flask app
if __name__ == "__main__":
    app.run()
