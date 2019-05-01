import pika

class RabbitConfig:
    RQ_COMMAND_USER = 'rabbitmq'
    RQ_COMMAND_PASS = 'rabbitmq'
    RQ_COMMAND_HOST = 'bjj-rabbit'
    RQ_COMMAND_PORT = 5672
    RQ_COMMAND_HEARTBEAT = 0

    UAEJJF_EVENT_RESULT = 'uaejjf_event_result'
    UAEJJF_PROFILE_INFO = 'uaejjf_profile_info'
    UAEJJF_EVENT_INFO = 'uaejjf_event_info'

    SMOOTHCOMP_EVENT_RESULT = 'smoothcomp_event_result'
    SMOOTHCOMP_PROFILE_INFO = 'smoothcomp_profile_info'
    SMOOTHCOMP_EVENT_INFO = 'smoothcomp_event_info'

    @staticmethod
    def get_rabbit_params():
        params = pika.URLParameters('amqp://rabbitmq:rabbitmq@bjj-rabbit:5672/%2F')
        return params