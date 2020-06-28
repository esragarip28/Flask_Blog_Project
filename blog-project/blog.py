
from flask import Flask ,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from functools import wraps
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import  sha256_crypt

app=Flask(__name__)
app.secret_key="erahalil28"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="esragarip"
app.config["MYSQL_DB"]="blog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql= MySQL(app)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("bu sayfaı goruntulemek için lutfen giris yapın","danger")
            return redirect(url_for("login"))    
    return decorated_function
#registration process:
class registrationForm(Form):
    fullname=StringField("isim",[validators.Length(min=4,max=25)])
    username=StringField("kullanıcı ismi",[validators.Length(min=4,max=25)])
    email = StringField('Email Addresi', [validators.Length(min=6, max=35)])
    password=PasswordField("Parola",[validators.DataRequired(),validators.EqualTo('confirm',message="Parola boş bırakılamaz")])
    confirm=PasswordField("Parolanızı tekrar giriniz")  
@app.route("/register", methods=["GET","POST"]) 
@login_required
def register():
    form =registrationForm(request.form)
    if request.method=="POST" and form.validate():
        fullname=form.fullname.data
        username=form.username.data
        email=form.email.data
        password=sha256_crypt.encrypt(form.password.data)
        cursor=mysql.connection.cursor()
        query="Insert into users(name,email,username,password),VALUES(%s,%s,%s,%s)"
        cursor.execute(query,(fullname,email,username,password))
        mysql.connection.commit()
        flash("Kayıt olma işlemi başarıyla gerçekleştirildi","success")
        return redirect(url_for("login"))
    else:
        return render_template(("register.html"),form=form)
#login:
class loginForm(Form):
    username=StringField("kullanıcı adı:")
    password=PasswordField("parola")

@app.route("/login",methods=["GET","POST"])
def login():
    form=loginForm(request.form)
    if request.method =="POST":
        username=form.username.data
        password=form.password.data
        cursor=mysql.connection.cursor()
        query="Select* from users where username=%s"
        result=cursor.execute(query,(username,))
        if result > 0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password,real_password):
                flash("Basarıyla giris yaptınız...","success")
                session["logged_in"] = True
                session["username" ]= username
                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlıs girdiniz...","danger")
                return redirect(url_for("login"))    
        else:
            flash("Böyle bir kullanıcı adı bulunmuyor...","danger")
            return redirect(url_for("login"))
    
    return render_template("login.html",form=form)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))    
class ArticlesForm(Form):
    title=StringField("Makale Başlığı",validators=[validators.Length(min=5,max=40)])
    author=StringField("Makale Yazarı",validators=[validators.Length(min=4,max=25)])
    content=TextAreaField("Makale içeriği",validators=[validators.Length(min=300)])
@app.route("/addarticles",methods=["GET","POST"])
@login_required
def addarticles():
    form=ArticlesForm(request.form)
    if request.method == "POST" and form.validate():
        title=form.title.data
        content=form.content.data
        author=form.author.data
        cursor=mysql.connection.cursor()
        sorgu="Insert into articles(title,author,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,author,content))
        mysql.connection.commit()
        cursor.close()
        flash("makale başarıyla eklendi...","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticles.html",form=form)




@app.route("/dashboard") #decorator...
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu="Select * From articles "
    result=cursor.execute(sorgu)
    if result > 0:
        articles=cursor.fetchall()
      
        return render_template("dashboard.html",articles=articles)

    else:
        return render_template("dashboard.html")
    return render_template("dashboard.html")
    
@app.route("/")
def index():
    cursor=mysql.connection.cursor()
    sorgu="Select * From articles where title='Bilgisayar Bilimi'"
    result=cursor.execute(sorgu)
    if result >0 :
        article=cursor.fetchone()
        return render_template("index.html",article=article)
    else:
        return render_template("index.html")    
    
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    cursor=mysql.connection.cursor()
    query="Select* From articles"
    result=cursor.execute(query)
    if result > 0:
        articles=cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")
@app.route("/articles/<string:id>")
def showArticle(id):
    cursor=mysql.connection.cursor()
    query="Select *From articles where id=%s"
    result=cursor.execute(query,(id,))
    
    if result >0:
        article=cursor.fetchone()
        return render_template("article.html",article=article)
    else:
        return render_template("articles.html")


#Delete Article:

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id=%s"
    result=cursor.execute(sorgu,(id,))
    if result > 0 :
        sorgu2="Delete from articles where id=%s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
       flash("boyle bir makale yok veya bu makaleyi silme yetkiniz yok..")
       return redirect(url_for("index"))
    return render_template("about.html")
    
@app.route("/articles/<string:id>")   
def article(id):
    return "article id: "+id

#Update Article
@app.route("/edit/<string:id>",methods=["GET","POST"])   
@login_required
def update(id):
    if request.method =="GET":
        cursor=mysql.connection.cursor()
        sorgu="Select* from articles where id =%s "
        result=cursor.execute(sorgu,(id,))  
        if result==0:
            flash("Böyle bir makale bulunmamaktadır...","danger")
            return redirect(url_for("index"))
        else:
            article=cursor.fetchone()
            form=ArticlesForm()
            form.title.data=article["title"]
            form.author.data=article["author"]
            form.content.data=article["content"]
            return render_template("update.html",form=form)

    else:
        #POST request:
        form=ArticlesForm(request.form)
        newTitle=form.title.data
        newAuthor=form.author.data
        newContent=form.content.data
        sorgu2="Update articles Set title=%s , content=%s , author=%s where id=%s"
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newTitle,newContent,newAuthor,id))
        mysql.connection.commit()
        flash("Makale başarıyla guncellendi...","success")
        return redirect(url_for("dashboard"))

 
#Search Article:
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method =="GET":
        return redirect(url_for("index"))
    else:
        keyword=request.form.get("keyword")
        cursor=mysql.connection.cursor()
        sorgu="Select* From articles Where title like '%"+keyword+"%'"
        result=cursor.execute(sorgu)
        if result == 0:
            flash("aranan kelimeye uygun makale bulunamadı..","warning")
            return redirect(url_for("articles"))
        else:
            articles=cursor.fetchall()
            return render_template("articles.html",articles=articles)    
   

if __name__ =="__main__":
        app.run(debug=True)    


