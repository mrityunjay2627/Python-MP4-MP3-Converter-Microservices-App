import pika, sys, os, time
import pika.connection
from pymongo import MongoClient
import gridfs
from converter import to_mp3

def main():
    client = MongoClient("host.minikube.internal", 27017) # Since cluster is in isolated network, to access our "localhost", we need to reference our system's network which is hosting the cluster as well as our MySQL Server.
    db_videos = client.videos # We get access to videos db and videos in our MongoDB database
    db_mp3s = client.mp3s

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    #rabbitmq
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq") # This is possible because our service name is "rabbitmq" and that will resolve to the host IP for our rabbitmq service
    )
    channel = connection.channel()


    # Whenever a message is taken off the queue by this consumer service, this callback function is going to be executed
    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch) # Start video conversion to mp3

        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag) # nack - not acknowledged. When we send this negative acknowledgement to the channel with this delivery_tag, rabbitmq knows which delivery_tag/message hasn't been acknowledged so it will know not to remove that message from the queue
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)


    # Create a configuration to consume the messages from our video queue
    channel.basic_consume(
        queue = os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
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
