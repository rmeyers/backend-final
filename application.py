from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Imported as login_session so it's not mixed up with session for sqlalchemy
from flask import session as login_session
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Initiate app
app = Flask(__name__)
app.url_map.strict_slashes = False

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "RM - Udacity Backend Final"

# Connect to Database and create database session
engine = create_engine('sqlite:///items.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Functio for the Google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    # Ensures that the user is making the request, and not a malicious script.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = result.get('error')
        flash(response)
        return render_template('error.html')

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is ' +
                                            'already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return redirect(url_for('showDashboard'))


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/disconnect')
def disconnect():
    # Only disconnect a connected user. <-- WHY?
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return redirect(url_for('homepage'))


# Check the login status of a user. Return 1 if
# logged in, 0 if not.
def check_login():
    # Check if the user is logged in.
    logged_in = 1
    if 'username' not in login_session:
        logged_in = 0
    return logged_in


######################################################################

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

######################################################################


# DB helper functions
def getItemsInCategory(category):
    category_id = session.query(Category).filter_by(category=category).one().id
    items = session.query(Item).filter_by(category_id=category_id)
    return items


def getRecentItems():
    items = session.query(Item).order_by(desc(Item.lastUpdate)).limit(10)
    return items


########################################################################
########################################################################


# Show homepage
@app.route('/')
def homepage():
    # This is an anti-forgery state token to stop attacks.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('index.html', STATE=state)


# Show all categories
@app.route('/dashboard')
def showDashboard():
    logged_in = check_login()
    categories = session.query(Category).order_by(asc(Category.category))
    items = getRecentItems()
    return render_template('dashboard.html', categories=categories,
                           items=items, logged_in=logged_in)


# Show items in a category
@app.route('/dashboard/<category>')
def showCategoryItems(category):
    logged_in = check_login()
    categories = session.query(Category).order_by(asc(Category.category))
    items = getItemsInCategory(category)
    return render_template('dashboard.html', categories=categories,
                           items=items, logged_in=logged_in)


# Show item information
@app.route('/<int:item_id>')
def showItem(item_id):
    logged_in = check_login()
    if logged_in == 0:
        return redirect('/')

    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=item, logged_in=logged_in)


# Allow editing of item
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def editItem(item_id):
    logged_in = check_login()
    if logged_in == 0:
        return redirect('/')
    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        if request.form['title']:
            item.item = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            category = request.form['category']
            category_id = session.query(Category).filter_by(category=category).one().id
            item.category_id = category_id
        session.add(item)
        session.commit()
        print 'Item edited successfully!'
        return redirect('/'+str(item_id))
    else:
        categories = session.query(Category).all()
        category_names = []
        for name in categories:
            category_names.append(name.category)
        category = session.query(Category).filter_by(id=item.category_id).one()
        return render_template('edit.html', item=item, category=category,
                               categories=category_names, logged_in=logged_in)


# Allow adding a new item
@app.route('/new', methods=['GET', 'POST'])
def newItem():
    logged_in = check_login()
    if logged_in == 0:
        return redirect('/dashboard')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        category_id = session.query(Category).filter_by(category=category)\
            .one().id
        user_id = login_session['user_id']
        newItem = Item(item=title, description=description,
                       lastUpdate=datetime.datetime.now(),
                       category_id=category_id, user_id=user_id)
        session.add(newItem)
        session.commit()
        print 'Item created successfully!'
        return redirect('/dashboard')
    else:
        categories = session.query(Category).all()
        category_names = []
        for name in categories:
            category_names.append(name.category)

        return render_template('newItem.html', categories=category_names,
                               logged_in=logged_in)


# Allow deleting of item
@app.route('/delete/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    logged_in = check_login()
    if logged_in == 0:
        return redirect('/')

    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        if request.form['_method'] == 'delete':
            session.delete(item)
            session.commit()
            print "Item deleted successfully!"
            return redirect('/dashboard')
    else:
        return render_template('delete.html', item=item, logged_in=logged_in)


# Making an API endpoint (GET request)
@app.route('/<int:item_id>/JSON')
def allItemsJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
