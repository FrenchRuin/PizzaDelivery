from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("mysql+pymysql://root:as2646@localhost:3306/pizzadelivery",
                       echo=True)
Base = declarative_base()

Session = sessionmaker()
