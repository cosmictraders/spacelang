import logging

import secret
from spacelang import File, load_text
from autotraders import session as s

if __name__ == "__main__":
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.basicConfig(format='[%(threadName)s] %(levelname)s: %(message)s', level=logging.DEBUG)
    File(load_text(open("example.yml"))).run(s.get_session(secret.TOKEN))
