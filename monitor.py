"""This script handles new files written to the directory specified by the OUTPUT_DIR environment variable.
"""
import os
import logging
import time
import json
from pymongo import MongoClient
from watchdog.observers.polling import PollingObserver 
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class Handler(FileSystemEventHandler):
    def __init__(self, mongo_host, mongo_port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = MongoClient(mongo_host, mongo_port)
        self._db = self._client.impact
        self._results = self._db.results

    def on_created(self, event):
        if event.src_path.endswith('.json'):
            file_path = event.src_path
            logger.info('New impact output: ' + file_path)
            time.sleep(5)
            for i in range(5):
                try:
                    with open(file_path, "r") as f:
                        document = json.load(f)
                        document["filename"] = file_path
                        search = self._results.find({"filename" : file_path})

                        if self._results.count_documents({"filename" : file_path}) == 0:
                            self._results.insert_one(document)
                            print(f"Processed {file_path}")
                        else:
                            print(f"{file_path} already processed.")
                        return
                except:
                    print(f"Error processing {file_path}")
                    time.sleep(5)


class Watcher:
    def __init__(self, directory, mongo_host, mongo_port):
        self.event_handler = Handler(mongo_host, mongo_port)
        self.observer = PollingObserver()
        self.observer.schedule(self.event_handler, directory, recursive=True)
        self.observer.start()

    def run(self):
        try:
            while True: 
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    MONGO_HOST = os.environ["MONGO_HOST"]
    MONGO_PORT = int(os.environ["MONGO_PORT"])
    OUTPUT_DIR = os.environ["OUTPUT_DIR"]
    watcher = Watcher(OUTPUT_DIR, MONGO_PORT, MONGO_HOST)
    watcher.run()
