import pika, sys, os, time
from send import email

def main():

    #rabbitmq
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq") # This is possible because our service name is "rabbitmq" and that will resolve to the host IP for our rabbitmq service
    )
    channel = connection.channel()


    # Whenever a message is taken off the queue by this consumer service, this callback function is going to be executed
    def callback(ch, method, properties, body):
        err = email.notification(body) # Start video conversion to mp3

        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag) # nack - not acknowledged. When we send this negative acknowledgement to the channel with this delivery_tag, rabbitmq knows which delivery_tag/message hasn't been acknowledged so it will know not to remove that message from the queue
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)


    # Create a configuration to consume the messages from our video queue
    channel.basic_consume(
        queue = os.environ.get("MP3_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
