from flask import Flask, render_template, request, flash, session, redirect
import re
import md5,os, binascii
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app,'The_Wall')
app.secret_key = 'This is not a secret key'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():                        
  return render_template('index.html') 

@app.route('/register', methods=["POST"])

def process_form():

  form_valid = True
  user = mysql.query_db('SELECT email from users WHERE email=:email ', {'email':request.form['email']})
  if user:
    flash('Duplicate email in database')
    form_valid = False
  # email address 
  if len(request.form['email']) <= 2:
    flash('email needs to be filled out')
    form_valid = False
  elif not EMAIL_REGEX.match(request.form['email']):
    flash("Invalid email")
    form_valid = False

  # first name validation
  if len(request.form['fname'])<2: 
    flash("first name needs at least two characters")
    form_valid = False
  elif not request.form["fname"].isalpha():
    flash("Invalid first name")
    form_valid = False

  # last name validation
  if len(request.form['lname'])<0:
    flash('last name field can not be empty')
    form_valid = False
  elif not request.form["lname"].isalpha():
    flash("Invalid last name")
    form_valid = False

  # password validation
  if len(request.form['password'])<8:
    flash('password field requires at least 8 characters')
    form_valid = False
  elif request.form['password'] != request.form['cpassword']:
    flash ('password do not match')
    form_valid = False

    # successful registration
  if form_valid:
    
    temp = request.form['password']
    salt =  binascii.b2a_hex(os.urandom(15))
    hash_pw = md5.new(temp + salt).hexdigest()

    query = "INSERT INTO users (first_name, last_name, email, password, pwsalt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :pwsalt, NOW(), NOW())"

    data = {
      'first_name': request.form['fname'],
      'last_name':  request.form['lname'],
      'email': request.form['email'],
      'password': hash_pw,
      'pwsalt': salt
    }
    myresult = mysql.query_db(query, data)
    return redirect('/wall')
  return redirect('/')

@app.route('/wall')
def wall():  
  query = "SELECT * from messages"
  results = mysql.query_db(query)                      
  return render_template('wall.html', messages=results) 

@app.route('/wall/messages/<user_id>', methods=['POST'])
def add_message(user_id):
  print session
  message_text = request.form['message']
  query = "INSERT INTO messages (messages, created_at, updated_at, user_id) VALUES (:message_text, Now(), Now(), :user_id)"
  data = { 
      'message_text': request.form['message'],
      'user_id': session['user']['id']
      
  }

  mysql.query_db(query, data)                       
  return redirect('/wall') 

# @app.route('wall/comments/<user_id>' methods=['POST'])
#   def add_comment(): 
#     message_comment = request.form['comments']
#     query = "INSERT INTO comments (comments, created_at, updated_at, user_id) VALUES (:message_text, Now(), Now(), :user_id)"
#     data = {
#         'messages_text': request.form['messages'],
#         'user_id': session['user']['id']
#     }
#     mysql.query_db(query, data)                       
#   return redirect('wall.html') 
@app.route('/')
def logout():
  session.clear()
  return redirect ('/')
app.run(debug=True)