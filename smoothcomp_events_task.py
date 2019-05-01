import pika
from crawler import *
from config import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(levelname)s %(message)s')

def events_task():
    connection = pika.BlockingConnection(parameters=RabbitConfig.get_rabbit_params())
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue = RabbitConfig.SMOOTHCOMP_EVENT_INFO, durable = True)
    channel.queue_declare(queue = RabbitConfig.SMOOTHCOMP_EVENT_RESULT, durable = True)

    events = smoothcomp_events("past")

    for event in events:
        event_url, event_date = event
        info_task = {
          "event_id" : event_url,
          "date" : event_date
        }

        result_task = {"event_id" : event_url.split("/")[-1]}

        channel.basic_publish(
            exchange='',
            routing_key = RabbitConfig.SMOOTHCOMP_EVENT_INFO,
            body = json.dumps(info_task, ensure_ascii=False),
            properties = pika.BasicProperties(delivery_mode=2)
        )

        channel.basic_publish(
            exchange='',
            routing_key = RabbitConfig.SMOOTHCOMP_EVENT_RESULT,
            body = json.dumps(result_task, ensure_ascii=False),
            properties = pika.BasicProperties(delivery_mode=2)
        )

events_task()
time.sleep(3600*24)