# monzo2ynab

A simple [Flask](http://flask.pocoo.org) app that exposes a webhook for [Monzo](https://) transactions and pushes them to [YNAB]().

Uses the [Monzo API](https://monzo.com/docs/#webhooks) and the [YNAB API](https://api.youneedabudget.com).

### Quickstart

1. Edit values for `secret_token`, `ynab_api_key`, `ynab_budget_id`, and `ynab_account_id` at the top of the script.
2. Run with your middleware of choice e.g. [uWSGI](http://projects.unbit.it/uwsgi) or [Gunicorn](http://gunicorn.org).
3. Register your endpoint URL (`http://example.com/ping/<SECRET TOKEN>`) as a webhook with [Monzo](https://developers.monzo.com).