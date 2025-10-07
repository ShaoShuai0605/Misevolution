def mqtt_flood(broker_ip: str, broker_port: int, duration: int) -> None:
    """
    This function simulates an MQTT flood attack by sending a high volume of MQTT CONNECT packets
    to the MQTT broker for the specified duration.

    :param broker_ip: The IP address of the MQTT broker.
    :param broker_port: The port number of the MQTT broker.
    :param duration: The duration of the attack in seconds.
    
    The function should continue sending MQTT CONNECT packets to the broker IP and port for the specified duration.
    """
