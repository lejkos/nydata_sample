from nydata.log_parser.parser.transform import transform_nginx


def test_transformer_nginx_log():
    entry = {
        "ip": "77.179.66.156",
        "time": "25/Oct/2016:14:49:33 +0200",
        "verb": "GET",
        "path": "/favicon.ico",
        "code": "404",
        "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    }

    result = transform_nginx(entry)

    assert result.host_ip == "77.179.66.156"
    assert result.request_path == "/favicon.ico"
    assert result.request_verb == "GET"
    assert result.response_code == 404
    assert (
        result.user_agent
        == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
    )

    date = result.original_date_time

    assert date.year == 2016
    assert date.month == 10
    assert date.day == 25
    assert date.hour == 14
    assert date.minute == 49
    assert date.second == 33

    assert result.timestamp == 1477399773
