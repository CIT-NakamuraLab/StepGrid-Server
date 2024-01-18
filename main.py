import logging

import uvicorn

from database import Base, engine
from server import app


def main():
    Base.metadata.create_all(engine)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] >> %(message)s')
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info', access_log=False)


if __name__ == "__main__":
    main()