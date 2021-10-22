"""This script populates the database with all files in the folder indicated by the OUTPUT_FOLDER directory. 
"""
from pymongo import MongoClient
import json
import dateutil.parser
import os 

logger = logging.getLogger(__name__)

def import_docs(mongo_host, mongo_port, output_dir):
    client = MongoClient(mongo_host, mongo_port)
    db = client.impact
    results = db.results

    impact_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]

    for filename in impact_files:
        with open(f"{output_dir}/{filename}", "r") as f:
            try:
                document = json.load(f)
                document["filename"] = filename

                # Remove this
                path_name = document["outputs"]["plot_file"]
                document["isotime"] = dateutil.parser.isoparse(document["isotime"])
                file_base = path_name.split("/")[-1]
                file_base = file_base.replace(":", "%3A")
                document["outputs"]["plot_file"] = f"https://raw.githubusercontent.com/jacquelinegarrahan/impact-grafana-mongodb/main/files/{file_base}"
                if results.count_documents({"filename" : filename}) == 0:
                    results.insert_one(document)
                    logger.info("Processed %s.", filename)
                else:
                    print("%s already processed.", filename)
            except:
                print("Error processing %s", filename)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    MONGO_HOST = os.environ["MONGO_HOST"]
    MONGO_PORT = int(os.environ["MONGO_PORT"])
    OUTPUT_DIR = os.environ["OUTPUT_DIR"]
    import_docs(MONGO_HOST, MONGO_PORT, OUPUT_DIR)


