from datetime import datetime, timedelta

import pytest

long_query = """query logs($dateFrom: Date!, $dateTo: Date!) { 
                                logs (date_from: $dateFrom, date_to: $dateTo) { 
                                    hostIP 
                                    timestamp 
                                    verb 
                                    path 
                                    code 
                                    userAgent 
                                }
                            }"""


ips_only_query = """query logs($dateFrom: Date!, $dateTo: Date!) { 
                                logs (date_from: $dateFrom, date_to: $dateTo) { 
                                    hostIP
                                }
                            }"""


@pytest.mark.usefixtures("db")
def test_query_from_task_pdf(db_setup_test_nginx_12, graphql_client):

    variables = {"dateFrom": "2000-11-11", "dateTo": "2019-12-12"}
    response = graphql_client.execute(long_query, variables=variables)

    assert "errors" not in response, response["errors"]

    logs = response["data"]["logs"]
    assert len(logs) == 12


@pytest.mark.usefixtures("db")
def test_query_from_task_pdf__only_ips(db_setup_test_nginx_12, graphql_client):

    variables = {"dateFrom": "2000-11-11", "dateTo": "2019-12-12"}
    response = graphql_client.execute(ips_only_query, variables=variables)

    assert "errors" not in response, response["errors"]

    logs = response["data"]["logs"]
    ips = sorted(set([log_entry["hostIP"] for log_entry in logs]))
    assert ips == ["127.0.0.1", "77.179.66.156"]


@pytest.mark.usefixtures("db")
def test_query_from_task_pdf__no_results(db_setup_test_nginx_12, graphql_client):

    variables = {"dateFrom": "2019-12-01", "dateTo": "2019-12-12"}
    response = graphql_client.execute(ips_only_query, variables=variables)

    assert "errors" not in response, response["errors"]

    logs = response["data"]["logs"]
    assert len(logs) == 0


def test_query_not_allowed__date_from_bigger_than_to(graphql_client):

    variables = {"dateFrom": "2090-10-10", "dateTo": "1970-01-01"}
    response = graphql_client.execute(ips_only_query, variables=variables)

    assert "errors" in response
    error = response["errors"][0]

    error_msg = "[!] Invalid query `date_from` always has to be smaller than `date_to`!"
    assert error["message"] == error_msg


@pytest.mark.usefixtures("db")
def test_query__dates_can_be_same_day(db_setup_test_nginx_12, graphql_client):

    variables = {"dateFrom": "2016-12-07", "dateTo": "2016-12-07"}
    response = graphql_client.execute(ips_only_query, variables=variables)

    assert "errors" not in response

    logs = response["data"]["logs"]
    assert len(logs) == 9


@pytest.mark.usefixtures("db")
def test_query__dates_can_be_same_day(db_setup_test_nginx_12, graphql_client):
    variables = {"dateFrom": "2016-01-01", "dateTo": "2016-11-30"}
    response = graphql_client.execute(long_query, variables=variables)

    assert "errors" not in response
    one_log = response["data"]["logs"][0]

    assert one_log["hostIP"] == "77.179.66.156"
    assert one_log["timestamp"] == 1477399773
    assert one_log["verb"] == "GET"
    assert one_log["path"] == "/"
    assert one_log["code"] == 200

    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36"
    assert one_log["userAgent"].startswith(agent)
