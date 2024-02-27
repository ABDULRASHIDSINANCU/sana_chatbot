from chatterbot import ChatBot
from flask import Flask, render_template, request,session,logging, url_for,redirect,flash,jsonify
from flask_recaptcha import ReCaptcha
import mysql.connector
import os
import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from datetime import datetime

app = Flask(__name__)

recaptcha = ReCaptcha(app=app)
app.secret_key=os.urandom(24)
app.static_folder = 'static'

#Google keys
app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6LdbAx0aAAAAAANl04WHtDbraFMufACHccHbn09L",
    RECAPTCHA_SECRET_KEY = "6LdbAx0aAAAAAMmkgBKJ2Z9xsQjMD5YutoXC6Wee"
))

recaptcha=ReCaptcha()
recaptcha.init_app(app)

#app.config['SECRET_KEY'] = 'cairocoders-ednalan'
# Replace 'your_database_url' with the actual URL to your database
#DATABASE_URL = 'mysql://sqluser:password@localhost/register'
DATABASE_URL = 'mysql://root:Mypassword@localhost/chatbot'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the User model to represent the 'users' table
class User(Base):
    __tablename__ = 'users'
    email = Column(String,primary_key=True)
    hint = Column(String)

#database connectivity
conn=mysql.connector.connect(host='localhost',port='3306',user='root',password='Mypassword',database='chatbot',auth_plugin='mysql_native_password')
cur=conn.cursor()

def make_key():
    return uuid.uuid4()

@app.route("/index")
def home():
    if 'id' in session:
        return render_template('index.html')
    else:
        return redirect('/')

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/register')
def about():
    return render_template('register.html')

# Route to get hint based on email

@app.route('/get_hint', methods=['GET'])
def get_hint():
    email = request.args.get('email')
    
    if not email:
        return jsonify({"error": "Email parameter is missing."}), 400

    # Query the database using SQLAlchemy
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()

    if user:
        hint = user.hint
    else:
        hint = "No hint available for this email."

    return jsonify({"hint": hint})


@app.route('/login_validation',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    cur.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email,password))
    users = cur.fetchall()
    if len(users)>0:
        loginTime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        #cur.execute("INSERT INTO logDetails (email, loginTime) VALUES (%s, %s)", (email, login_time))
        cur.callproc('LoginProc', (email, loginTime))
        conn.commit()
        session['id']=users[0][0]
        flash('You were successfully logged in')
        return redirect('/index')
    else:
        flash('Invalid credentials !!!')
        return redirect('/')
    # return "The Email is {} and the Password is {}".format(email,password)
    # return render_template('register.html')

@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('name') 
    email=request.form.get('uemail')
    password=request.form.get('upassword')
    hint=request.form.get('hint')

    #cur.execute("UPDATE users SET password='{}'WHERE name = '{}'".format(password, name))
    cur.execute("""INSERT INTO  users(name,email,password,hint) VALUES('{}','{}','{}','{}')""".format(name,email,password,hint))
    conn.commit()
    cur.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
    myuser=cur.fetchall()
    flash('You have successfully registered!')
    #loginTime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    #cur.callproc('LoginProc', (email, loginTime))
    #conn.commit()
    session['id']=myuser[0][0]
    return redirect('/index')

@app.route('/suggestion',methods=['POST'])
def suggestion():
    email=request.form.get('uemail')
    suggesMess=request.form.get('message')

    cur.execute("""INSERT INTO  suggestion(email,message) VALUES('{}','{}')""".format(email,suggesMess))
    conn.commit()
    flash('You suggestion is succesfully sent!')
    return redirect('/index')

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')  
    #return str(ChatBot.get_response(userText))
    return get_output(userText)

def get_output(input_text):
    return data.get(input_text, "Output not found")

@app.route('/enrollment',methods=['POST'])
def enroll():
    email=request.form.get('mail')
    mobile=request.form.get('mob')
    colg=request.form.get('prevColg')
    grade=request.form.get('grade')
    enquiry=request.form.get('enq')
    course=request.form.get('corse')
    state=request.form.get('state')
    dob=request.form.get('dob')
    name=request.form.get('fullname')
    adres=request.form.get('address')
    gend=request.form.get('gender')

    cur.execute("""INSERT INTO  candpersnldetls(name,email,phone,dob,addresss,gender) VALUES('{}','{}','{}','{}','{}','{}')""".format(name,email,mobile,dob,adres,gend))
    conn.commit()
    cur.execute("""INSERT INTO  enrollment(email,mobile,college,grade,enquiry,course,state) VALUES('{}','{}','{}','{}','{}','{}','{}')""".format(email,mobile,colg,grade,enquiry,course,state))
    conn.commit()
    flash('You have succesfully Enrolled !')
    return redirect('/index')

data = {
    "Hi": "Hello!",
    "1": "<b>BTech <br>The following are frequently searched terms related to student. Please select one from the options below: <br> <br> 1.1 Admission <br>1.2 Fee <br>1.3 Scholarship <br>1.4 Placement <br>1.5 Hostel <br>1.6 Contact Details </b>",
    "1.1": "<b> Admission <br> <br> 1.1.1 Documents Required <br> 1.1.2 Sanctioned Intake <br> 1.1.3 Last Rank </b>",
    "1.1.1": "<b> 1.1.1 Documents Required <br><br> → Admit Card, Allotment Memo, and Candidates' Data Sheet issued by the CEE (Student keeps original).<br> → Fee remittance receipt from the bank (Student keeps original).<br> → SSLC Certificate / Xth Mark List & Pass Certificate (Original & one photocopy).<br> → Qualifying Examination Certificate (Plus Two / VHSC / THS / Diploma) (Original & one photocopy).<br> → Community / Nativity / Income Certificate for reservation category (Original).<br> → Transfer Certificate (Original).<br> → Conduct Certificate (obtained within 6 months).<br> → Physical/Medical Fitness Certificate. </b>",
    "1.1.2": "<b> 1.1.2 Sanctioned Intake <br><br>  1.1.2.1 Civil Engineering (CE) <br> 1.1.2.2 Computer Science and Engineering (CSE) <br> 1.1.2.3 Electronics and Communications Engineering (ECE) <br> 1.1.2.4 Electrical and Electronics Engineering (EEE) <br> 1.1.2.5 Information Technology (IT) <br> 1.1.2.6 Mechanical Engineering (ME) </b>",
    "1.1.2.1": "<b> Civil Engineering (CE) <br><br> → Sanctioned : 67 <br> → Merit : 46 <br> → Management : 15 <br> → Fee Waiver : 3 <br> → NRI : 3 </b>",
    "1.1.2.2": "<b> Computer Science and Engineering (CSE) <br><br> → Sanctioned : 132 <br> → Merit : 46 <br> → Management : 54 <br> → Fee Waiver : 6 <br> → NRI : 6 </b>",
    "1.1.2.3": "<b> Electronics and Communications Engineering (ECE) <br><br> → Sanctioned : 64 <br> → Merit : 46 <br> → Management : 15 <br> → Fee Waiver : 0 <br> → NRI : 3 </b>",
    "1.1.2.4": "<b> Electrical and Electronics Engineering (EEE) <br><br> → Sanctioned : 64 <br> → Merit : 46 <br> → Management : 15 <br> → Fee Waiver : 0 <br> → NRI : 3 </b>",
    "1.1.2.5": "<b> Information Technology (IT) <br><br> → Sanctioned : 34 <br> → Merit : 17 <br> → Management : 13 <br> → Fee Waiver : 2 <br> → NRI : 2 </b>",
    "1.1.2.6": "<b> Mechanical Engineering (ME) <br><br> → Sanctioned : 64 <br> → Merit : 46 <br> → Management : 15 <br> → Fee Waiver : 0 <br> → NRI : 3 </b>",
    "1.1.3": "<b> 1.1.3 Last Rank <br><br>  1.1.3.1 Phase-1 <br> 1.1.3.2 Phase-2 <br> 1.1.3.3 Phase-3 </b>",
    "1.1.3.1": "<b> 1.1.3.1 Phase-1 <br><br>  1.1.3.1.1 Civil Engineering (CE) <br> 1.1.3.1.2 Computer Science and Engineering (CSE) <br> 1.1.3.1.3 Electronics and Communications Engineering (ECE) <br> 1.1.3.1.4 Electrical and Electronics Engineering (EEE) <br> 1.1.3.1.5 Information Technology (IT) <br> 1.1.3.1.6 Mechanical Engineering (ME) </b>",
    "1.1.3.1.1": "<b> Civil Engineering (CE) <br><br> → Sm : 25640  <br> → Ew : 60524 <br> → Ez : 29592  <br> → Mu : 29004 <br> → Bh : 29254 <br> → La : 49561 <br> → Dv : (No information provided) <br> → Vk : 29786 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 57094 <br> → St : (No information provided) <br> → Fw : 15708 <br> → Mg : 47844 </b>",
    "1.1.3.1.2": "<b> Computer Science and Engineering (CSE) <br><br> → Sm : 9949  <br> → Ew : 14814 <br> → Ez : 11479  <br> → Mu : 11632 <br> → Bh : 11168 <br> → La : 39971 <br> → Dv : 12280 <br> → Vk : 19336 <br> → Bx : 31416 <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 44329 <br> → St : 54707 <br> → Fw : 6309 <br> → Mg : 23902 </b>",
    "1.1.3.1.3": "<b> Electronics and Communications Engineering (ECE) <br><br> → Sm : 17265  <br> → Ew : 24216 <br> → Ez : 21005  <br> → Mu : 20034 <br> → Bh : 18550 <br> → La : (No information provided) <br> → Dv : 33838 <br> → Vk : 31189 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 49637 <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 39641 </b>",
    "1.1.3.1.4": "<b> Electrical and Electronics Engineering (EEE) <br><br> → Sm : 35595  <br> → Ew : (No information provided) <br> → Ez : 38977  <br> → Mu : 39973 <br> → Bh : 46440 <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 55637 <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 57880 </b>",
    "1.1.3.1.5": "<b> Information Technology (IT) <br><br> → Sm : 18180  <br> → Ew : 23457 <br> → Ez : 19610  <br> → Mu : 20469 <br> → Bh : 19610 <br> → La : 20469 <br> → Dv : 27361 <br> → Vk : 48207 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 51656 <br> → St : (No information provided) <br> → Fw : 13825 <br> → Mg : 31194 </b>",
    "1.1.3.1.6": "<b> Mechanical Engineering (ME) <br><br> → Sm : 36534  <br> → Ew : 53359 <br> → Ez : 45882  <br> → Mu : 46262 <br> → Bh : 38498 <br> → La : 37753 <br> → Dv : 60200 <br> → Vk : 46827 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 58181 <br> → St : (No information provided) <br> → Xs : 50446 <br> → Fw : (No information provided) <br> → Mg : 60558 </b>",
    "1.1.3.2": "<b> 1.1.3.2 Phase-2 <br><br>  1.1.3.2.1 Civil Engineering (CE) <br> 1.1.3.2.2 Computer Science and Engineering (CSE) <br> 1.1.3.2.3 Electronics and Communications Engineering (ECE) <br> 1.1.3.2.4 Electrical and Electronics Engineering (EEE) <br> 1.1.3.2.5 Information Technology (IT) <br> 1.1.3.2.6 Mechanical Engineering (ME) </b>",
    "1.1.3.2.1": "<b> Civil Engineering (CE) <br><br> → Sm : 37127  <br> → Ew : (No information provided) <br> → Ez : 46419  <br> → Mu : 43492 <br> → Bh : 37301 <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : 58411 <br> → Mg : 18059 </b>",
    "1.1.3.2.2": "<b> Computer Science and Engineering (CSE) <br><br> → Sm : 12018  <br> → Ew : 19561 <br> → Ez : 15742  <br> → Mu : 13200 <br> → Bh : 14366 <br> → La : 52298 <br> → Dv : 12280 <br> → Vk : 19336 <br> → Bx : 37953 <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 53991 <br> → St : 54707 <br> → Oe : 57218 <br> → Fw : 6922 <br> → Mg : 29590 </b>",
    "1.1.3.2.3": "<b> Electronics and Communications Engineering (ECE) <br><br> → Sm : 24099  <br> → Ew : 30273 <br> → Ez : 28057  <br> → Mu : 31469 <br> → Bh : 27887 <br> → La : (No information provided) <br> → Dv : 33838 <br> → Vk : 31189 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 49637 <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 43003 </b>",
    "1.1.3.2.4": "<b> Electrical and Electronics Engineering (EEE) <br><br> → Sm : 54657  <br> → Ew : (No information provided) <br> → Ez : 55964  <br> → Mu : 59122 <br> → Bh : 57729 <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 55637 <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 49092 </b>",
    "1.1.3.2.5": "<b> Information Technology (IT) <br><br> → Sm : 24817  <br> → Ew : 25669 <br> → Ez : 25940  <br> → Mu : 27519 <br> → Bh : 27361 <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : 16338 <br> → Mg : 37025 </b>",
    "1.1.3.2.6": "<b> Mechanical Engineering (ME) <br><br> → Sm : 57927  <br> → Ew : (No information provided) <br> → Ez : (No information provided)  <br> → Mu : 60558 <br> → Bh : (No information provided) <br> → La : (No information provided) <br> → Dv : 60200 <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : (No information provided) </b>",
    "1.1.3.3": "<b> 1.1.3.3 Phase-3 <br><br>  1.1.3.3.1 Civil Engineering (CE) <br> 1.1.3.3.2 Computer Science and Engineering (CSE) <br> 1.1.3.3.3 Electronics and Communications Engineering (ECE) <br> 1.1.3.3.4 Electrical and Electronics Engineering (EEE) <br> 1.1.3.3.5 Information Technology (IT) <br> 1.1.3.3.6 Mechanical Engineering (ME) </b>",
    "1.1.3.3.1": "<b> Civil Engineering (CE) <br><br> → Sm : 60337  <br> → Ew : (No information provided) <br> → Ez : (No information provided)  <br> → Mu : (No information provided) <br> → Bh : (No information provided) <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : 23461 <br> → Mg : 48086 </b>",
    "1.1.3.3.2": "<b> Computer Science and Engineering (CSE) <br><br> → Sm : 12581  <br> → Ew : 23138 <br> → Ez : 17541  <br> → Mu : 13997 <br> → Bh : 14735 <br> → La : 52298 <br> → Dv : 21469 <br> → Vk : 19336 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 53919 <br> → St : 54707 <br> → Oe : 57218 <br> → Fw : 6922 <br> → Mg : 33793 </b>",
    "1.1.3.3.3": "<b> Electronics and Communications Engineering (ECE) <br><br> → Sm : 38919  <br> → Ew : 41921 <br> → Ez : 57081 <br> → Mu : 41855 <br> → Bh : 43441 <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : 43549 <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : 49637 <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 60035 </b>",
    "1.1.3.3.4": "<b> Electrical and Electronics Engineering (EEE) <br><br> → Sm : 55964  <br> → Ew : (No information provided) <br> → Ez : (No information provided)  <br> → Mu : (No information provided) <br> → Bh : (No information provided) <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 49092 </b>",
    "1.1.3.3.5": "<b> Information Technology (IT) <br><br> → Sm : 27576  <br> → Ew : (No information provided) <br> → Ez : 42657  <br> → Mu : 33008 <br> → Bh : (No information provided) <br> → La : 36063 <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : 33793 </b>",
    "1.1.3.3.6": "<b> Mechanical Engineering (ME) <br><br> → Sm : 66673  <br> → Ew : (No information provided) <br> → Ez : (No information provided)  <br> → Mu : 60558 <br> → Bh : (No information provided) <br> → La : (No information provided) <br> → Dv : (No information provided) <br> → Vk : (No information provided) <br> → Bx : (No information provided) <br> → Ku : (No information provided) <br> → Kn : (No information provided) <br> → Sc : (No information provided) <br> → St : (No information provided) <br> → Fw : (No information provided) <br> → Mg : (No information provided) </b>",
    "1.2": "<b> Fee <br> <br> → Tuition Fee : INR 60,000 / annum <br> → Special Fee : INR 25,000 / annum </b>",
    "1.3": "<b> Scholarship <br> <br> → Merit Scholarship : Merit-cum-Means Scholarships (for Minority Students) <br> → Other Scholarship : Central Sector Scholarship, KSCSTE Scholarship </b>",
    "1.4": "<b> Placement <br> <br> → Placement Percentage : 76.9% <br> → Highest Package : INR 12.5 LPA <br> → Average Package : INR 4.5 LPA </b>",
    "1.5": "<b> Hostel <br> <br> → Hostel Available : Yes <br> → Hostel Fee : INR 30,000 / annum </b>",
    "1.6": "<b> Contact Details <br> <br> → Phone : +91-470-XXX-XXXX <br> → Email : principal@xxxxxxxx.ac.in </b>",
    "1.2": "<b> 1.2 Fee <br> <br> 1.2.1 Tuition Fee <br> 1.2.2 Miscellaneous Fee </b>",
    "1.2.1": "<b> 1.2.1 Tuition Fee <br> <br> 1.2.1.1 Merit Seat <br> 1.2.1.2 Management Seat <br> 1.2.1.3 NRI Seat </b>",
    "1.2.1.1": "<b> Merit Seat <br><br> → Tuition Fee : 35000  <br> → Admission Fee : 250 <br> → Special Fee : 1200  <br> → Caution Deposit : 5000 <br> → Establishment Charges : 1500 <br> → Fee already paid to Entrance Commissioner : 10000 <br> → Student Administration Fee : 1050 <br> → Arts and Sports Fee : 530 <br> → Examination Fee : 5000 <br> → Students Insurance Premium : 220 <br> → Student Affiliation Fee : 750 <br> → Total : 40500 </b>",
    "1.2.1.2": "<b> Management Seat <br><br> → Tuition Fee : 65000  <br> → Admission Fee : 250 <br> → Special Fee : 1200  <br> → Caution Deposit : 5000 <br> → Establishment Charges : 1500 <br> → Fee already paid to Entrance Commissioner : 10000 <br> → Student Administration Fee : 1050 <br> → Arts and Sports Fee : 530 <br> → Examination Fee : 5000 <br> → Students Insurance Premium : 220 <br> → Student Affiliation Fee : 750 <br> → Total : 70500 </b>",
    "1.2.1.3": "<b> NRI Seat <br><br> → Admission Fee : 250 <br> → Tuition Fee : 100000  <br> → Special Fee : 1200  <br> → Caution Deposit : 5000 <br> → Refundable Deposit : 125000 <br> → Establishment Charges : 1500 <br> → University Administration Fee : 1000 <br> → University Examination Fee : 3400 <br> → Arts and Sports Fee : 500 <br> → Insurance : 220 <br> → Total : 238070 </b>",
    "1.2.2": "<b> 1.2.2 Miscellaneous Fee <br> <br> 1.2.2.1 Merit and Management Seats <br> 1.2.2.2 NRI Seat </b>",
    "1.2.2.1": "<b> Merit and Management Seats <br><br> → PTA Membership Fee : 5000 <br> → Department Association Fee : 1000 <br> → Career Guidance and Placement : 500  <br> → Co-operative Society : 1500 <br> → Physical Fitness : 250 <br> → Identity Card + Series Examination Fees : 350 <br> → College Union Fee : 1200 <br> → Total : 9800 </b>",
    "1.2.2.2": "<b> NRI Seat <br><br> → PTA : 5000 <br> → Co-operative Society : 1500 <br> → Department Association Fee : 1000 <br> → Career Guidance and Placement : 500 <br> → Physical Fitness : 250 <br> → Identity Card Fee : 100 <br> → College Union Fee : 1200 <br> → Total : 9550 </b>",
    "1.3": "<b> 1.3 Scholarship <br> <br> 1.3.1 Merit-cum-Means (MCM) <br> 1.3.2 e-grantz <br> 1.3.3 CH Muhammed Koya </b>",
    "1.3.1": "<b> 1.3.1 Merit-cum-Means (MCM) <br> 1.3.1.1 Eligibility Criteria <br> 1.3.1.2 Documents Required </b>",
    "1.3.1.1": "<b> Eligibility Criteria <br><br> → Students from minority communities, including Muslims, Christians, Sikhs, Buddhists, Jains, Zoroastrians, and Parsis, are eligible for this scheme. <br> → They must obtain at least 50% marks or a grade equivalent in their last final examination. <br> → The gross annual income of their parents must not surpass ₹ 2,50,000. <br> → Students must pursue their course from India in an affiliated school, institution, college or university. <br> → The minimum duration of their course should be 1 year. </b>",
    "1.3.1.2": "<b> Documents Required <br><br> → Domicile certificate from the respective state. <br> → Self-declaration of belonging to a minority community. <br> → Self-attested copy of previous academic mark sheet. <br> → Copy of Aadhar Enrollment or Aadhar Card. <br> → Income certificate issued by the designated state/UT authority. <br> → Proof of bank account in the student's name or a joint account with either parent. <br> → Student's photograph. </b>",
    "1.3.2": "<b> 1.3.2 e-grantz <br> 1.3.2.1 Eligibility Criteria <br> 1.3.2.2 Documents Required </b>",
    "1.3.2.1": "<b> Eligibility Criteria <br><br> → The applicants should be domiciled in Kerala. <br> → They should be studying at the post-matriculation level from any recognized college/ board. <br> → The applicants should not secure at least 75% at the end of each month. <br> → They should have taken admission under the merit and reservation quota. <br> → Students from SC, OBC, OEC, and other socially/economically backward communities are eligible to apply. <br> → Candidates should be pursuing various courses such as degree, diploma, doctoral, higher secondary, polytechnic, postgraduate, professional, and VHSE. <br> → The candidates should be pursuing a degree, diploma, doctoral, higher secondary, polytechnic, postgraduate, professional and VHSE courses. <br> → The candidates belonging to SC and OEC categories do not have any annual family income limitations. <br> → The annual family income limit is INR 1,00,000 for OBC students and other categories. </b>",
    "1.3.2.2": "<b> Documents Required <br><br> → Marksheets <br> → College ID <br> → Bank Details <br> → Caste Certificate <br> → Income Certificate <br> → Proof of admission <br> → Domicile certificate <br> → Aadhar card/ PAN card </b>",
    "1.3.3": "<b> 1.3.3 CH Muhammed Koya <br> 1.3.3.1 Eligibility Criteria <br> 1.3.3.2 Documents Required </b>",
    "1.3.3.1": "<b> Eligibility Criteria <br><br> → They must be domiciles of Kerala. <br> → They should be enrolled in a government or government-aided institution. <br> → Female candidates must belong to the Muslim, converted Christian, or Latin community. <br> → They should be pursuing graduation or higher studies. <br> → They must have obtained at least 50% marks in their previous qualifying examination. <br> → The annual family income should not exceed INR 8,00,000. <br> → Candidates who have enrolled in self-financing colleges based on merit seats or after attempting the common entrance exam are eligible as well. <br> → They should have a bank account in a nationalized bank to receive the scholarship amount. <br> → Students applying for the hostel stipend should reside in a government-recognized hostel. </b>",
    "1.3.3.2": "<b> Documents Required <br><br> → Domicile certificate <br> → Caste Certificate <br> → Aadhaar Card <br> → SSLC marksheet (or equivalent exam) <br> → Income Certificate  <br> → Bank details from a nationalized bank include the account number and IFSC code. </b>",
    "1.4": "<b> Placement 2022-23 <br><br> → Cognizant : 27 <br> → EY : 9 <br> → Infosys : 1 <br> → QBurst : 6 <br> → Quest Global : 7 <br> → TCS : 3 <br> → Acabes : 4 <br> → Tenzotech : 11 <br> → GadgEon : 2 <br> → ULTS : 8 </b>",
    "1.5": "<b> Hostel <br><br> → Admission Fee : 250 <br> → Mess Deposit : 6000 <br> → Caution Deposit : 1000 <br> → Establishment charge : 1000 <br> → Total : 2250 </b>",
    "1.6": "<b> 1.6 Contact Details <br><br>  1.6.1 Civil Engineering (CE) <br> 1.6.2 Computer Science and Engineering & Information Technology (CSE - IT) <br> 1.6.3 Electronics and Communications Engineering (ECE) <br> 1.6.4 Electrical and Electronics Engineering (EEE) <br> 1.6.5 Mechanical Engineering (ME) </b>",
    "1.6.1": "<b> Civil Engineering (CE) <br><br> → HOD : Prof. Dr. Anjali M S <br> → Phone : 9496251434 <br> → Email : ced@lbscek.ac.in </b>",
    "1.6.2": "<b> Computer Science and Engineering & Information Technology (CSE - IT) <br><br> → HOD : Prof. Dr. Anver S R <br> → Phone : 9447341312 <br> → Email : csed@lbscek.ac.in </b>",
    "1.6.3": "<b> Electronics and Communications Engineering (ECE) <br><br> → HOD : Prof. Dr. Mary Reena <br> → Phone : 9745306534 <br> → Email : eced@lbscek.ac.in </b>",
    "1.6.4": "<b> Electrical and Electronics Engineering (EEE) <br><br> → HOD : Prof. Jayakumar M <br> → Phone : 9446463953 <br> → Email : eed@lbscek.ac.in </b>",
    "1.6.5": "<b> Mechanical Engineering (ME) <br><br> → HOD : Prof. Vinod O M <br> → Phone : 9446389436 <br> → Email : med@lbscek.ac.in </b>",
    "2": "<b>MTech <br>The following are frequently searched terms related to student . Please select one from the options below : <br> <br> 2.1 Admission <br> 2.2  Fee <br> 2.3  Scholarship <br> 2.4 Hostel </b>",
    "2.1": "<b>  Admission <br> <br> 2.1.1 Documents Required <br> 2.1.2 Sanctioned Intake </b>",
    "2.1.1": "<b> 2.1.1 Documents Required <br><br> → SSLC Certificate / 10th Mark List & Pass Certificate (Original & photocopy). <br> → Qualifying Examination Certificate (Plus Two / VHSC / THS / Diploma) (Original & photocopy). <br> → Physical/Medical Fitness Certificate. <br> → Statement of Marks of B.Tech (up to 6th Semester). <br> → BTech Passing Certificate. <br> → Conduct Certificate <br> → Transfer Certificate <br> → GATE Scorecard (if applicable). <br> → Reservation Category Certificates (Community/Nativity/Income Certificate) (Original) </b>",
    "2.1.2": "<b> 2.1.2 Sanctioned Intake <br><br>  2.1.2.1 Computer Science and Information Security <br> 2.1.2.2 VLSI Design and Signal Processing </b>",
    "2.1.2.1": "<b> Computer Science and Information Security <br><br> → Sanctioned : 18 </b>",
    "2.1.2.2": "<b> VLSI Design and Signal Processing <br><br> → Sanctioned : 18 </b>",
    "2.2": "<b> 2.2 Fee <br> <br> 2.2.1 Tuition Fee <br> 2.2.2 Miscellaneous Fee </b>",
    "2.2.1": "<b> Tuition Fee <br><br> → Tuition Fee : 12000  <br> → Admission Fee : 650 <br> → Caution Deposit : 3500 <br> → Establishment Charges : 1500 <br> → Student Administration Fee : 1040 <br> → Arts and Sports Fee : 530 <br> → Examination Fee : 1500 <br> → Students Insurance Premium : 220 <br> → Student Affiliation Fee : 1000 <br> → Total : 21940 </b>",
    "2.2.2": "<b> Miscellaneous Fee <br><br> → PTA Membership Fee : 5000 <br> → Department Association Fee : 1000 <br> → Career Guidance and Placement : 500  <br> → Physical Fitness : 250 <br> → Identity Card Fee : 100 <br> → College Union Fee : 1200 <br> → Total : 8050 </b>",
    "2.3": "<b> GATE Scholarship <br> 2.3.1 Eligibility Criteria <br> 2.3.2 Documents Required </b>",
    "2.3.1": "<b> Eligibility Criteria <br><br> → Valid GATE scorecard at the time of admission and application before the admission deadline. <br> → Admission to an AICTE-approved Postgraduate Institution in programs like Master of Engineering, Master of Technology, Master of Architecture, or Master of Pharmacy. <br> → Full-time student status in the mentioned programs. <br> → Possession of a personal general saving bank account (not a joint account). <br> → No receipt of monetary assistance, scholarships, salary, stipend, etc., from any other source during study in the Institute. <br> → Completion of an 8/10-hour teaching and research-related activity assigned by the Institute. <br> → Eligibility for SC/ST/OBC (Non-creamy layer)/Physically Handicapped/Differently Abled candidates, with a valid caste certificate. Students without a valid certificate will not be considered eligible. <br> → Eligibility extends to applicants from India, Bangladesh, Nepal, Sri Lanka, Ethiopia, and the United Arab Emirates. </b>",
    "2.3.2": "<b> Documents Required <br><br> → GATE scorecard <br> → Valid ID photo proof <br> → PDF copy of the passbook <br> → Aadhaar card (J&K, Meghalaya, and Assam students exempted) <br> → PDF copy of the caste certificate <br> → PDF copy of the Non-Creamy Layer (NCL) certificate for OBC candidates (not older than 1 year) <br> → Signature in running handwriting </b>",
    "2.4": "<b> Hostel <br><br> → Admission Fee : 250 <br> → Mess Deposit : 6000 <br> → Caution Deposit : 1000 <br> → Establishment charge : 1000 <br> → Total : 2250 </b>",
    "Bye": "Have a good day!",
    "bye": "Have a good day!"

}

if __name__ == "__main__":
    # app.secret_key=""
    app.run(debug=True) 