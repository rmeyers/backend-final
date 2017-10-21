from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item

engine = create_engine('sqlite:///items.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Items in Soccer
category1 = Category(category = "Soccer")

session.add(category1)
session.commit()


item1 = Item(item = "Ball", user_id = 0, description = "Used to score points", category = category1)

session.add(item1)
session.commit()

item2 = Item(item = "Running shoes", user_id = 0, description = "This is needed to kick the ball and protect feet!", category = category1)

session.add(item2)
session.commit()

item3 = Item(item = "Clothes", user_id = 0, description = "Lets keep it decent.", category = category1)

session.add(item3)
session.commit()



category2 = Category(category = "Basketball")

session.add(category2)
session.commit()


item1 = Item(item = "Basketball", user_id = 0, description = "The ball needed to play the game", category = category2)

session.add(item1)
session.commit()

item2 = Item(item = "Hoops", user_id = 0, description = "Otherwise, where else would you score points!", category = category2)

session.add(item2)
session.commit()

item3 = Item(item = "Shoes", user_id = 0, description = "Gotta grip that court well.", category = category2)

session.add(item3)
session.commit()


category1 = Category(category = "Baseball")

session.add(category1)
session.commit()


item1 = Item(item = "Bat", user_id = 0, description = "Best bat around, send your hits out of the park!", category = category1)

session.add(item1)
session.commit()

item2 = Item(item = "Field", user_id = 0, description = "Over 5 acres in size, with bases for running. All set to go.", category = category1)

session.add(item2)
session.commit()

item3 = Item(item = "Glove", user_id = 0, description = "The Yankees play with these gloves.", category = category1)

session.add(item3)
session.commit()


category1 = Category(category = "Frisbee")

session.add(category1)
session.commit()


item1 = Item(item = "Frisbee", user_id = 0, description = "This is basically all you need.", category = category1)

session.add(item1)
session.commit()


category1 = Category(category = "Snowboarding")

session.add(category1)
session.commit()


item1 = Item(item = "Snowboard", user_id = 0, description = "Will make you go fast down the mountain", category = category1)

session.add(item1)
session.commit()

item2 = Item(item = "Snow", user_id = 0, description = "no fun on the grass", category = category1)

session.add(item2)
session.commit()

item3 = Item(item = "Coat", user_id = 0, description = "Super warm so you won't get cold.", category = category1)

session.add(item3)
session.commit()


category1 = Category(category = "Rock Climbing")

session.add(category1)
session.commit()


item1 = Item(item = "Wall", user_id = 0, description = "Gotta climb something.", category = category1)

session.add(item1)
session.commit()

item2 = Item(item = "Rope", user_id = 0, description = "World's strongest rope.", category = category1)

session.add(item2)
session.commit()


category1 = Category(category = "Foosball")

session.add(category1)
session.commit()

item9 = Item(item = "Foosball Table", user_id = 0, description = "Best foosball table around. Made for high performance.", category = category1)

session.add(item9)
session.commit()


print "added menu items!"

