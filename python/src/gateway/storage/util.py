import pika, json

import pika.spec

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f) # Put file in mongodb. Return file id (fid)
    except Exception as err:
        return "Mongodb internal server error", 500
    
    message = { # Python Object (Dictionary here)
        "video_file_id": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish( # Put this message into rabbitmq queue
            exchange="",
            routing_key="video", # It is actually going to be name of our queue
            body=json.dumps(message), # Python Object to JSON
            properties=pika.BasicProperties( # To retain/persist messages in rabbitmq queue in the event of pods fail or crash and restart/spinoff
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except:
        fs.delete(fid) # Since there is no message to downstreams service, this file will get stale in our database and never get processed. So, delete it.
        return "Message not published to rabbitmq - internal server error", 500