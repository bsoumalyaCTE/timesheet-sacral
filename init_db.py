
from configs.database import engine, Base
from configs.models import *


Base.metadata.create_all(bind=engine)