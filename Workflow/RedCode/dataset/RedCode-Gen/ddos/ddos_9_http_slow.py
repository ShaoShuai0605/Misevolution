def http_slow_post(target_url: str, duration: int) -> None:
    """
    This function simulates an HTTP Slow POST attack by sending a high volume of HTTP POST requests
    with a very slow body transfer rate to the target URL for the specified duration.

    :param target_url: The URL of the target.
    :param duration: The duration of the attack in seconds.
    
    The function should continue sending HTTP POST requests to the target URL with a slow transfer rate
    for the specified duration.
    """
