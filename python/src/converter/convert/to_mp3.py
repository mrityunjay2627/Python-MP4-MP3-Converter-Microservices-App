import pika, json, tempfile, os
from bson.objectid import ObjectId
from moviepy import VideoFileClip
import pika.spec

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message) #  message from queue

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message['video_fid'])) # converting video file id from string (gateway/storage/util.py) to object id, from where we will extract the video contents

    # add video contents to empty temp file
    tf.write(out.read()) 

    # convert video file to audio
    audio = VideoFileClip(tf.name).audio # tf.name wil resolve to the path of that temp file

    tf.close() # temp file will be deleted automatically

    # write audio to a file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3" # We want to create path for our audio file. We will get the directories on our OS where these temp files are being stored by this tempfile module. And we append our choice of file name along with that path/
    audio.write_audiofile(tf_path)  # temp file created by write_audiofile method

    # Save audio file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data) # Store data in MongoDB
    f.close()
    os.remove(tf_path) # Since this file is created by audio.write_audiofile module, we need to delete it manually

    # update message
    message['mp3_fid'] = str(fid)

    # put the message in queue
    try:
        channel.basic_publish(
            exchange = "",
            routing_key = os.environ.get("MP3_QUEUE"),
            body = json.dumps(message),
            properties = pika.BasicProperties(
                delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid) # if we can't add message in queue, delete the file from mongodb since our app will do the whole process again.
        return"failed to publish message"

