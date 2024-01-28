from flask import Flask, render_template, request, redirect, flash
from flask_pymongo import pymongo
from bson.objectid import ObjectId
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


CONNECTION_STRING = "mongodb+srv://Andrea:mongoDB@cluster0.1xyx1kr.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database("blog")
article_collection = pymongo.collection.Collection(db, "articles")
user_collection = pymongo.collection.Collection(db, "users")

app = Flask(__name__)
app.secret_key = "super secret key"


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Set the login view for Flask-Login
# login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, _id, username, email, password, is_admin, date_of_registration):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.date_of_registration = date_of_registration

    def get_id(self):
        return str(self._id)

    def save(self):
        user_collection.insert_one(
            {
                "_id": self._id,
                "username": self.username,
                "email": self.email,
                "password": self.password,
                "is_admin": self.is_admin,
                "date_of_registration": self.date_of_registration,
            }
        )

    @staticmethod
    def get(user_id):
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return User(
            str(user["_id"]),
            user["username"],
            user["email"],
            user["password"],
            user["is_admin"],
            user["date_of_registration"],
        )


# define a user_loader function
@login_manager.user_loader
def load_user(user_id):
    # load and return a user object using the user_id
    return User.get(user_id)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.users.find_one({"email": email})
        if user and password == user["password"]:
            user_object = User(
                user["_id"],
                user["username"],
                user["email"],
                user["password"],
                user["is_admin"],
                user["date_of_registration"],
            )
            login_user(user_object)
            if user["is_admin"]:
                return redirect("/admin_home")
            else:
                return redirect("/home")
        else:
            flash("Invalid email or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(("/"))


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        is_admin = 0
        date_of_registration = datetime.date.today().strftime("%d/%m/%Y")

        user = db.users.find_one({"email": email})
        if user:
            flash("Tento email sa už používa.", category="error")
            print("nasli sme usera s tymto mailom")
        elif len(email) < 3:
            flash("Email musí mať viac ako 3 písmená.", category="error")
        elif len(username) < 1:
            flash("Meno musí mať viac ako 1 písmeno.", category="error")
        elif password1 != password2:
            flash("Heslá sa nezhodujú", category="error")
        elif len(password1) < 1:
            flash("Heslo musí mať aspoň 2 písmená.", category="error")
        else:
            # hashed_password = generate_password_hash(password1, method='sha256')
            result = user_collection.insert_one(
                {
                    #'_id': ObjectId(),
                    "email": email,
                    "username": username,
                    "password": password1,
                    "is_admin": is_admin,
                    "date_of_registration": date_of_registration,
                }
            )
            print("Sme tu")
            new_user = User(
                result.inserted_id,
                username,
                email,
                password1,
                is_admin,
                date_of_registration,
            )

            # login_user(new_user, remember=True)

            flash("Účet bol úspešne vytvorený. Prihláste sa.", category="success")
            print("Účet bol úspešne vytvorený.")

            return redirect("/")

    return render_template("sign_up.html")


@app.route("/home")
@app.route("/home/page/")
@app.route("/home/page/<int:page_num>")
@login_required
def home(page_num=1):
    per_page = 3
    total_articles = db.articles.count_documents({})
    total_pages = (total_articles + per_page - 1) // per_page

    start_index = (page_num - 1) * per_page
    end_index = start_index + per_page
    articles = list(
        db.articles.find().sort("_id", -1).skip(start_index).limit(per_page)
    )
    users = list(db.users.find())

    print(current_user.username)

    return render_template(
        "home.html",
        articles=articles,
        users=users,
        page_num=page_num,
        total_pages=total_pages,
        user=current_user,
    )


@app.route("/admin_home")
@app.route("/admin_home/page/")
@app.route("/admin_home/page/<int:page_num>")
@login_required
def admin_home(page_num=1):
    per_page = 3
    total_articles = db.articles.count_documents({})
    total_pages = (total_articles + per_page - 1) // per_page

    start_index = (page_num - 1) * per_page
    end_index = start_index + per_page
    articles = list(
        db.articles.find().sort("_id", -1).skip(start_index).limit(per_page)
    )
    users = list(db.users.find())

    print(current_user.username)

    return render_template(
        "admin_home.html",
        articles=articles,
        users=users,
        page_num=page_num,
        total_pages=total_pages,
        user=current_user,
    )


@app.route("/my_blogs")
@app.route("/my_blogs/page/")
@app.route("/my_blogs/page/<int:page_num>")
@login_required
def my_blogs(page_num=1):
    per_page = 3
    total_articles = db.articles.count_documents({})
    total_pages = (total_articles + per_page - 1) // per_page

    start_index = (page_num - 1) * per_page
    end_index = start_index + per_page

    articles = list(
        db.articles.find({"author": current_user._id})
        .sort("date", -1)
        .skip(start_index)
        .limit(per_page)
    )
    print(len(articles))

    return render_template(
        "my_blogs.html",
        articles=articles,
        users=user_collection,
        page_num=page_num,
        total_pages=total_pages,
        user=current_user,
    )


# vytvoriť záznam
@app.route("/create", methods=("GET", "POST"))
def create():
    categories = []
    # vkladanie záznamu cez formulár pre zadefinované atribúty
    if request.method == "POST":
        the_date = datetime.date.today()
        formatted_date = the_date.strftime("%d/%m/%Y")
        #  _id = int(request.form['_id'])
        title = request.form["title"]
        author = request.form["author"]
        date = formatted_date
        text = request.form["text"]
        categories = request.form.getlist("categories[]")
        image = request.form["image"]
        if not image:
            image = "https://images.unsplash.com/flagged/photo-1554757388-5982229b9ce7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"
        article_collection.insert_one(
            {
                #  "_id": _id,
                "title": title,
                "author": (author),
                "date": date,
                "text": text,
                "categories": categories,
                "image": image,
            }
        )
        if current_user.is_admin == 0:
            return redirect("/my_blogs")
        else:
            return redirect("/admin_home")
    else:
        return render_template("create.html", user=current_user)


# upraviť záznam
@app.route("/<_id>/update/", methods=("GET", "POST"))
# nájdenie konkrétneho záznamu podľa _id
def update(_id):
    article = db.articles.find_one({"_id": ObjectId(_id)})
    if article:
        selected_categories = article["categories"]
    else:
        selected_categories = []

    print(selected_categories)
    categories = []
    # upravenie záznamu cez formulár pre zadefinované atribúty
    if request.method == "POST":
        the_date = datetime.date.today()
        formatted_date = the_date.strftime("%d/%m/%Y")
        # _id = ObjectId(request.form['_id'])
        title = request.form["title"]
        author = request.form["author"]
        date = formatted_date
        text = request.form["text"]
        categories = request.form.getlist("categories[]")
        image = request.form["image"]
        article_collection.update_one(
            {"_id": ObjectId(_id)},
            {
                "$set": {
                    "title": title,
                    "author": (author),
                    "date": date,
                    "text": text,
                    "categories": categories,
                    "image": image,
                }
            },
        )
        if current_user.is_admin == 0:
            return redirect("/my_blogs")
        else:
            return redirect("/admin_home")
    else:
        return render_template(
            "update.html",
            article=article,
            selected_categories=selected_categories,
            user=current_user,
        )


# vymazať záznam
@app.route("/<_id>/delete/", methods=("GET", "POST"))
# nájdenie konkrétneho záznamu podľa _id
def delete(_id):
    article_collection.delete_one({"_id": ObjectId(_id)})
    if current_user.is_admin == 0:
        return redirect("/my_blogs")
    else:
        return redirect("/admin_home")


@app.route("/<_id>/delete_user/", methods=("GET", "POST"))
# nájdenie konkrétneho záznamu podľa _id
def delete_user(_id):
    user_collection.delete_one({"_id": ObjectId(_id)})

    # vymazeme aj jeho articles
    found_articles_ids = []
    articles = db.articles.find()

    for article in articles:
        if article["author"] == str(_id):
            found_articles_ids.append(article["_id"])

    for article_id in found_articles_ids:
        article_collection.delete_one({"_id": ObjectId(article_id)})

    # vymazeme aj jeho comments
    comments_to_delete = []  # Store comment IDs here

    # Iterate over articles again to find comments
    articles = db.articles.find()
    for article in articles:
        comments = article.get(
            "comments", []
        )  # Retrieve the 'comments' field or an empty list if it doesn't exist
        for comment in comments:
            print(comment)
            if str(comment["author_id"]) == str(_id):
                comments_to_delete.append(comment["_id"])
                print("comment id added to comments_to_delete")

    # Delete comments
    for comment_id in comments_to_delete:
        print("to delete", comment_id)
        db.articles.update_one(
            {"comments._id": ObjectId(comment_id)},
            {"$pull": {"comments": {"_id": ObjectId(comment_id)}}},
        )
        print("comment deleted")

    return redirect("/user_list")


@app.route("/articles/<article_id>/add-comment", methods=["POST"])
@login_required
def add_comment(article_id):
    # Get the current user's ID
    current_user_id = current_user._id

    # Get the text of the submitted comment
    comment_text = request.form["comment_text"]
    comment_id = ObjectId()

    if not isinstance(current_user_id, ObjectId):
        current_user_id = ObjectId(current_user_id)

    the_date = datetime.date.today()
    formatted_date = the_date.strftime("%d/%m/%Y")
    # Create a new Comment dictionary
    comment_dict = {
        "_id": comment_id,
        "text": comment_text,
        "date": formatted_date,
        "author_id": ObjectId(current_user_id),
    }

    # Add the new Comment dictionary to the Article document's "comments" array
    db.articles.update_one(
        {"_id": ObjectId(article_id)}, {"$push": {"comments": comment_dict}}
    )

    # Redirect back to the article page
    return redirect(f"/article_detail/{article_id}")


@app.route("/article_detail/<article_id>", methods=["GET", "POST"])
def article_detail(article_id):
    print(article_id)
    article = db.articles.find_one({"_id": ObjectId(article_id)})
    users = db.users.find()
    return render_template(
        "article_detail.html",
        article=article,
        users=users,
        user_collection=user_collection,
        ObjectId=ObjectId,
        current_user=current_user,
    )


@app.route(
    "/article_detail/<article_id>/delete-comment/<comment_id>", methods=["GET", "POST"]
)
@login_required
def delete_comment(article_id, comment_id):
    print(comment_id)
    if request.method == "POST":
        print("sme v delete comment pathe")
        # Delete the comment from the Article document's "comments" array
        db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$pull": {"comments": {"_id": ObjectId(comment_id)}}},
        )

        # Redirect back to the article page

    return redirect(f"/article_detail/{article_id}")


@app.route("/user_list")
@login_required
def user_list():
    users = db.users.find()
    return render_template("user_list.html", users=users)


@app.route("/dashboard")
@login_required
def dashboard():
    # Fetch data from MongoDB and format it for the chart
    data = []
    users = db.users.find({"is_admin": 0})
    for user in users:
        articles_count = db.articles.count_documents({"author": str(user["_id"])})

        data.append({"label": user["username"], "value": articles_count})

    # Render a template that includes the chart
    return render_template("dashboard.html", data=data)
