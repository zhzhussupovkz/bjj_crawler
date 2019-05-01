import pika
from crawler import *
from config import *

connection = pika.BlockingConnection(parameters=RabbitConfig.get_rabbit_params())
channel = connection.channel()
channel.basic_qos(prefetch_count=1)
channel.queue_declare(queue = RabbitConfig.UAEJJF_PROFILE_INFO, durable = True)

def save_to_db(ch, method, properties, body):
    body = json.loads(body)
    profile_id = body.get("profile_id")
    profile = uaejjf_parse_profile(profile_id)
    uaejjf_save_profile(profile)
    ch.basic_ack(delivery_tag = method.delivery_tag)

def run():
    channel.basic_consume(on_message_callback = save_to_db, queue = RabbitConfig.UAEJJF_PROFILE_INFO)
    channel.start_consuming()

run()