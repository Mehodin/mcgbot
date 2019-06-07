import tinydb, dotenv, os, logging
import roles

dotenv.load_dotenv()
db = tinydb.TinyDB("db.json")

class State:
    def __init__(self):
        fmt_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        if os.getenv("PRODUCTION") == "true":
            logging.basicConfig(format=fmt_string, level=logging.WARNING)
            print("Running in production mode")
            self.production = True
        else:
            logging.basicConfig(format=fmt_string, level=logging.INFO)
            print("Running in debug mode")
            self.production = False

        self.teams_db = db.table("teams")
        self.role_map = roles.get_role_map(self.production)
