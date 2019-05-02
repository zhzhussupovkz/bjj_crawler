import pika
from crawler import *
from config import *

connection = pika.BlockingConnection(parameters=RabbitConfig.get_rabbit_params())
channel = connection.channel()
channel.basic_qos(prefetch_count=1)
channel.queue_declare(queue = RabbitConfig.SMOOTHCOMP_EVENT_INFO, durable = True)

def save_to_db(ch, method, properties, body):
    body = json.loads(body)
    event_id = body.get("event_id")
    date = body.get("date")
    event = (event_id, date)
    event = smoothcomp_get_event(event)
    smoothcomp_save(event)
    ch.basic_ack(delivery_tag = method.delivery_tag)

def run():
    channel.basic_consume(on_message_callback = save_to_db, queue = RabbitConfig.SMOOTHCOMP_EVENT_INFO)
    channel.start_consuming()

run()