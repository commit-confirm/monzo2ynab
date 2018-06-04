#!/usr/bin/env python3
import os
import json
import logging
import requests
import boto3

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# Load variables
try:
    ynab_base_url = os.environ["YNAB_BASE_URL"]
    ynab_api_key = os.environ["YNAB_API_KEY"]
    ynab_budget_id = os.environ["YNAB_BUDGET_ID"]
    ynab_account_id = os.environ["YNAB_ACCOUNT_ID"]
    monzo_account_id = os.environ["MONZO_ACCOUNT_ID"]
except KeyError:
    logger.error("Environmental variables failed to load")
    respond(KeyError("Environmental variables failed to load"))


def respond(err, res=None):
    return {
        "statusCode": "400" if err else "200",
        "body": err.message if err else json.dumps(res),
        "headers": {"Content-Type": "application/json"},
    }


def lambda_handler(event, context):
    operation = event["httpMethod"]
    if operation == "POST":
        logger.info("Received POST request")
        payload = json.loads(event["body"])
        if payload["data"]["account_id"] == monzo_account_id:
            logger.info("Payload contains valid Monzo accound ID")
            try:
                payee = payload["data"]["merchant"]["name"]
            except TypeError:
                try:
                    payee = payload["data"]["counterparty"]["name"]
                except TypeError:
                    payee = payload["data"]["description"]

            transaction = {
                "transaction": {
                    "account_id": ynab_account_id,
                    "date": payload["data"]["created"],
                    "amount": (payload["data"]["amount"] * 10),
                    "payee_name": payee,
                    "cleared": "Cleared",
                    "import_id": "Monzo:{}:{}".format(
                        (payload["data"]["amount"]), payload["data"]["created"]
                    ),
                }
            }
            logger.info("Transaction prepared: {}".format(transaction))
            with requests.Session() as s:
                s.headers.update({"Authorization": "Bearer {}".format(ynab_api_key)})
                try:
                    logger.info("Posting to YNAB...")
                    r = s.post(
                        "{}/budgets/{}/transactions".format(
                            ynab_base_url, ynab_budget_id
                        ),
                        json=transaction,
                    )
                except requests.exceptions.RequestException as e:
                    logger.error("Failed to post to YNAB: {}".format(e))
                    return respond(e, None)
            logger.info("Posted transaction to YNAB. Response: {}".format(r))
            return respond(None, r.json())
        else:
            logger.error("Wrong Monzo account ID provided")
            return respond(ValueError("Wrong Monzo account id"))
    else:
        logger.error("Unsupported API method")
        return respond(ValueError("Unsupported method"))
