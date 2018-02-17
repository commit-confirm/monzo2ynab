#!/usr/bin/env python3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config.update(
    DEBUG = False,
    TESTING = False
)

secret_token = ""
ynab_base = "https://api.youneedabudget.com/v1"
ynab_api_key = ""
ynab_budget_id = ""
ynab_account_id = ""

@app.route('/')
def root():
    return 'OK'

@app.route('/ping/{}'.format(secret_token), methods=['POST'])
def ping():
    try:
        payee = request.json['data']['merchant']['name']
    except TypeError:
        try:
            payee = request.json['data']['counterparty']['name']
        except TypeError:
            payee = request.json['data']['description']
    
    transaction = {
        "transaction": {
            "account_id": ynab_account_id,
            "date": request.json['data']['created'],
            "amount": (request.json['data']['amount']*10),
            "payee_name": payee,
            "cleared": "Cleared",
            "import_id": "Monzo:{}:{}".format((request.json['data']['amount']), request.json['data']['created'])
        }
    }
    with requests.Session() as s:
        s.headers.update({'Authorization': 'Bearer {}'.format(ynab_api_key)})
        try:
            r = s.post('{}/budgets/{}/transactions'.format(ynab_base, ynab_budget_id), json=transaction)
        except requests.exceptions.RequestException as e:
            return e
    return jsonify(r.json())

if __name__ == '__main__':
    app.run()