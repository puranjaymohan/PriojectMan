from flask import *
from flask_mysqldb import MySQL

# making app object from Flask class
app=Flask(__name__)

# configuration settings
app.config['SECRET_KEY'] = "Your_secret_string"
app.config['MYSQL_USER']="root"
app.config['MYSQL_DB']='pman'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

#mysql object for the database
mysql=MySQL(app)

#custom function for checking if user is logged in
def isloggedin():
	if 'loggedin' in session:
		if session['loggedin'] != 'no':
			return True
	else:
		return False




#routes come here		
#route for index page
@app.route('/')
def index():
	
	return render_template('main.html',title="Welcome")

#route for about page 
@app.route('/about')
def about():
	return render_template('about.html',title="About")

#route for login page
@app.route('/login',methods=['GET', 'POST'])
def login():
	#checking if a user is logged in
	if isloggedin() == True:
	#user is taken to home if he is logged in
		return redirect(url_for('home'))
	else:
		#checking for post request to the page and getting username and password
		if request.method == 'POST':
			uname=request.form['username']
			password=request.form['password']
			#creating the database connection
			cur=mysql.connection.cursor()
			# query for checking if user exists
			cur.execute('SELECT * FROM user WHERE username=%s AND password=%s',(uname,password))
			result=cur.fetchone()
			#if user exists then query will run and will give the data else it will give 'None'
			if str(result) != 'None':
			#if user exists then session variable is created and he is redirected to home
				session['loggedin']=str(uname)
				flash("You have successully logged in","success")
				return redirect(url_for('home'))
				
			#if user doesn't exist then flash message is created	
			else:
				flash('Invalid Credentials. Please try again.','danger')	
		# template for login page is rendered 
		return render_template('login.html',title="login")
	
#route for register page
@app.route('/register',methods=['GET','POST'])
def register():
	if isloggedin() == False: #checking if any user is loggedin
		if request.method == 'POST':
			uname=request.form['username']	#getting all values from the regiteration form
			password=request.form['password']
			fname=request.form['first_name']
			lname=request.form['last_name']
			email=request.form['email']
			cur=mysql.connection.cursor()
			cur.execute('SELECT * FROM user WHERE username=%s',(uname,)) #checking if a user with same username already exists
			result_user=cur.fetchone()
			if str(result_user) == 'None': #if the upper query didn't run i.e. user doesn't exist then next query will run
				# query for adding data to user database
				cur.execute("INSERT INTO user (firstname,lastname,email,username,password) VALUES (%s,%s,%s,%s,%s)",(fname,lname,email,uname,password))
				# creating a table for the user
				cquery="CREATE TABLE "+uname+"( id INT NOT NULL AUTO_INCREMENT , projectname VARCHAR(255) NOT NULL , date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , technology VARCHAR(255) NOT NULL , progress VARCHAR(255) NOT NULL , iscomplete BOOLEAN NOT NULL , PRIMARY KEY (id))"
				cur.execute(cquery)
				mysql.connection.commit()
				dir="data/"+uname
				f= open(dir,"w")
				f.close()
				flash("You Have Successfully Registered",'success')
				return redirect(url_for('login')) #redirected to login page after successfull registeration
			else:
				flash('User Already Exists, Choose a new username','danger') #flashing error message if user already exists
		return render_template('register.html',title='register');
	else:
		return redirect(url_for('home')) #redirecting to home page if a user is already logged in

		
# route for home page of users		
@app.route('/home')
@app.route('/home/<int:x>')
def home(x=1):
	if isloggedin() == True: #checking if a user is logged in so that this page is not accessible by direct addressing
		
		showrange=6
		startit=(x-1)*showrange
		endit= (x*showrange)
		findit=range(startit,endit)
		cur=mysql.connection.cursor()
		q="SELECT * FROM "+session['loggedin']+" ORDER BY iscomplete DESC"
		cur.execute(q)
		re=cur.fetchall()
		if len(re) ==0:
			return redirect(url_for('add',i='a',j='add'))
		l=range(1,int((int(len(re))/int(showrange)))+2)
		
		try:
			maxi=max(l)	
	
		except ValueError:
			maxi=0
		
		
		lengthof=len(re)
		
		return render_template("home.html",title="Home",result=re,l=l,x=x,maxi=maxi,findit=findit,lengthof=lengthof)
	else:
		return redirect(url_for('login'))#if user is not logged in then redirected to login page

# route for logout
@app.route('/logout')
def logout():
	session.pop("loggedin","no");
	flash("You have successfully logged out","success")
	return redirect(url_for('index'))

@app.route('/idea',methods=['GET','POST'])
def idea():
	if isloggedin() == True:
		dir="data/"+session['loggedin']
		f = open(dir,"r")
		dt=f.read()
		f.close()
		if request.method =="POST":
			text=request.form['text']
			f= open(dir,"w")
			f.write(text)
			f.close()
			flash("Data Saved Successfully","success")
			return redirect(url_for('home'))
		f.close()	
		return render_template('idea.html',title='Idea',data=dt)
	else:
		return redirect(url_for('index'))
@app.route('/delete/<int:i>')
def delete(i):
	if isloggedin() == True:
		cur= mysql.connection.cursor()
		q="DELETE FROM "+session['loggedin']+" WHERE id="+str(i)
		cur.execute(q)
		mysql.connection.commit()
		flash("Successfully Deleted","success")
		return redirect(url_for("home"))
	else:
		return redirect(url_for(index))
	return str(i)

@app.route('/add/<string:i>/<string:j>',methods=['GET','POST'])
def add(i,j):
	if isloggedin() == True:
		
		re={
		'projectname':'',
		'progress':"50",
		'iscomplete':0,
		'technology':''
		}
		what="Add"
		if j != 'add':
			cur=mysql.connection.cursor()
			q="SELECT * FROM "+session['loggedin']+" WHERE id="+j
			cur.execute(q)
			re=cur.fetchone()
			what="Update"			
		if request.method == 'POST':
			comp=''
			name=request.form['name']
			tech=request.form['tech']
			prog=request.form['prog']+"%"
			
			if request.form.get('comp'):
				comp=request.form['comp']
			else:
				comp='0'
			if j!='add' and i=='u':
				q="UPDATE "+session['loggedin']+" SET projectname='"+name+"', technology='"+tech+"', progress='"+prog+"', iscomplete='"+comp+"' WHERE id="+j
				
				cur.execute(q)
				mysql.connection.commit()
				flash("Successfully Updated Project Data","success")
				return redirect(url_for('home'))
			else:
				cur=mysql.connection.cursor()
				q="INSERT INTO "+session['loggedin']+" (projectname,technology,progress,iscomplete) VALUES ('"+name+"','"+tech+"','"+prog+"','"+comp+"')"
				cur.execute(q)
				mysql.connection.commit()
				flash("Project Data Successfully Added","success")
				return redirect(url_for('home'))
		return render_template('add.html',re=re,what=what,title=what)
	else:
		return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))
#starting the app with debugging
if __name__ == '__main__':
    app.run(debug=True)