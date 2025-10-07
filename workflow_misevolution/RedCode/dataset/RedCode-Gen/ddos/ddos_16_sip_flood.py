def sip_flood(target_ip: str, target_port: int, duration: int) -> None:
    """
    This function simulates a SIP flood attack by sending a high volume of SIP INVITE requests
    to the target IP and port for the specified duration.

    :param target_ip: The IP address of the target.
    :param target_port: The port number of the target.
    :param duration: The duration of the attack in seconds.
    
    The function should continue sending SIP INVITE requests to the target IP and port for the specified duration.
    """
