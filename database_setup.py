from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


# ADD YOUR USER MODEL HERE
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False)
    picture = Column(String(250))


# Create the category table (sports listed here)
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    category = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'category': self.category,
            'id': self.id,
        }


# Create the sports items table, link to categories, add
# serialize function for the API endpoint
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    item = Column(String(80), nullable=False)
    lastUpdate = Column(String(80), onupdate=datetime.datetime.now)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'item': self.item,
            'description': self.description,
            'lastUpdate': self.lastUpdate,
            'category': self.category_id,
            'user': self.user_id
        }


engine = create_engine('sqlite:///items.db')

Base.metadata.create_all(engine)
