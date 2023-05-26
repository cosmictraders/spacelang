import secret
from spacelang import File, load_text
from autotraders import session as s

if __name__ == "__main__":
    File(load_text(open("example.yml"))).run(s.get_session(secret.TOKEN))
