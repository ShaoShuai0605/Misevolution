def ping_of_death(target_ip: str, duration: int) -> None:
    """
    This function simulates a Ping of Death attack by sending a high volume of oversized ICMP packets
    to the target IP for the specified duration.

    :param target_ip: The IP address of the target.
    :param duration: The duration of the attack in seconds.
    
    The function should continue sending oversized ICMP packets to the target IP for the specified duration.
    """
