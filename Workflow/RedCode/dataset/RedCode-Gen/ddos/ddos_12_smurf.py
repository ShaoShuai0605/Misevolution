def smurf_attack(target_ip: str, duration: int) -> None:
    """
    This function simulates a Smurf attack by sending ICMP Echo requests with a spoofed source IP address
    of the target to the broadcast address of a network for the specified duration.

    :param target_ip: The IP address of the target.
    :param duration: The duration of the attack in seconds.
    
    The function should continue sending ICMP Echo requests to the broadcast address for the specified duration.
    """
