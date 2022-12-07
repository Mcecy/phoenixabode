from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image
from io import BytesIO
import os

from helpers import error, login_required, admin_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///phoenixabode.db")


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if session.get("user_id") is not None:
        return redirect("/novels")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return error("Must provide username.", 403)
        # Ensure password was submitted
        elif not password:
            return error("Must provide password.", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return error("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        if rows[0]["is_staff"] == "true":
            session["is_staff"] = True

        session["username"] = username.upper()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_id") is not None:
        return redirect("/novels")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if password != confirm:
            return error("Password mismatch", 400)
        if username == "" or password == "" or confirm == "":
            return error("Empty field", 400)

        usernames = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(usernames) < 1:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
            if not username or not password:
                return error("Missing username and/or password", 400)
            return redirect("/login")
        else:
            return error("Username taken")
    else:
        return render_template("register.html")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form.get("username")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_password):
            return error("invalid username and/or password", 403)
        else:
            db.execute("UPDATE users SET hash = ? WHERE username = ?", generate_password_hash(new_password), username)
        return redirect("/login")
    else:
        return render_template("change_password.html")


@app.route("/novels")
@login_required
def novels():
    novels = db.execute("SELECT N.id, N.title, A.name, N.status FROM novels N JOIN authors A ON A.id = N.author_id")
    for row in novels:
        novel_id = int(row["id"])
        chapters = db.execute("SELECT COUNT(C.chapter_number) AS chapters FROM chapters C JOIN novels N ON N.id = C.novel_id WHERE N.id = ?", novel_id)
        row["chapters"] = chapters[0]["chapters"]

    return render_template("novels.html", novels=novels)


@app.route("/")
def index():
    novels = db.execute("SELECT title FROM novels")
    return render_template("index.html", novels=novels)


@app.route("/read/<title>", methods=["GET", "POST"])
@login_required
def read(title):
    if request.method == "POST":
        title = title.lower()
        user_id = session.get("user_id")
        library = db.execute("SELECT N.id, N.title, L.user_id FROM novels N LEFT OUTER JOIN library L ON L.novel_id = N.id WHERE L.user_id = ? AND N.title = ?", user_id, title)

        if len(library) > 0:
            novel_id = library[0]["id"]
            db.execute("DELETE FROM library WHERE novel_id = ? AND user_id = ?", novel_id, user_id)
        else:
            novel_id = db.execute("SELECT id FROM novels WHERE title = ?", title)
            novel_id = int(novel_id[0]["id"])
            db.execute("INSERT INTO library (novel_id, user_id) VALUES (?, ?)", novel_id, user_id)

        return redirect(f"/library/{user_id}")
    else:
        chapters = db.execute("SELECT C.id, C.title FROM chapters C JOIN novels N ON N.id = C.novel_id WHERE N.title = ?", title)
        author = db.execute("SELECT A.name FROM authors A JOIN novels N ON N.author_id = A.id WHERE N.title = ?", title)
        sinopsis = db.execute("SELECT sinopsis FROM novels WHERE title = ?", title)
        sinopsis = sinopsis[0]["sinopsis"]
        author = author[0]["name"]

        return render_template("read.html", title=title, author=author, sinopsis=sinopsis, chapters=chapters)


@app.route("/library/<user_id>")
@login_required
def library(user_id):
    novels = db.execute("SELECT N.id, N.title, A.name, N.status, L.user_id FROM novels N JOIN authors A ON A.id = N.author_id LEFT OUTER JOIN library L ON L.novel_id = N.id WHERE L.user_id = ?", user_id)

    if len(novels) > 0:
        for row in novels:
            novel_id = int(row["id"])
            chapters = db.execute("SELECT COUNT(C.chapter_number) AS chapters FROM chapters C JOIN novels N ON N.id = C.novel_id WHERE N.id = ?", novel_id)
            row["chapters"] = chapters[0]["chapters"]

        return render_template("library.html", novels=novels)
    else:
        return render_template("library.html")


@app.route("/read/<title>/<chapter_id>")
@login_required
def read_chapter(title, chapter_id):
    chapter = db.execute("SELECT C.title, C.content FROM chapters C JOIN novels N ON N.id = C.novel_id WHERE C.id = ? AND N.title = ?", chapter_id, title)
    chapter_title = chapter[0]["title"]
    content = chapter[0]["content"].split("\n")
    return render_template("chapter.html", chapter_title=chapter_title, title=title, content=content)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        content = request.form.get("search")
        if content != "":
            novels = db.execute(f"SELECT N.id, N.title, N.chapter_count, A.name, N.status FROM novels N JOIN authors A ON A.id = N.author_id WHERE N.title LIKE '%{content}%'")
            if len(novels) > 0:
                check = 0
                return render_template("search.html", novels=novels, check=check)
        return render_template("search.html", message="Nothing found")
    else:
        return render_template("search.html")


@app.route("/post", methods=["GET", "POST"])
@admin_required
def post():
    if request.method == "POST":
        novel = request.form.get("novel_title").lower()
        chapter_number = int(request.form.get("chapter_number"))
        chapter_title = request.form.get("chapter_title")
        content = request.form.get("content")

        if novel != "" and chapter_number != "" and chapter_title != "":
            checks = db.execute("SELECT N.id, C.chapter_number FROM novels N LEFT OUTER JOIN chapters C ON C.novel_id = N.id WHERE N.title = ?", novel)
            print(checks)
            if len(checks) < 1:
                return error("Invalid novel title", 400)
            for chapter in checks:
                try:
                    if chapter_number == int(chapter["chapter_number"]):
                        return error("Chapter number already exists", 400)
                except Exception:
                    break
            novel_id = checks[0]["id"]
            db.execute("INSERT INTO chapters (novel_id, title, chapter_number, content) VALUES (?, ?, ?, ?)", novel_id, chapter_title, chapter_number, content)
            chapter_id = db.execute("SELECT id FROM chapters WHERE title = ?", chapter_title)
            chapter_id = chapter_id[0]["id"]
            return redirect(f"/read/{novel.lower()}/{chapter_id}")
        else:
            return error("One or more fields are missing", 400)
    else:
        return render_template("post.html")


@app.route("/new_novel", methods=["GET", "POST"])
@admin_required
def new_novel():
    if request.method == "POST":
        novel = request.form.get("title").lower()
        author = request.form.get("author").lower()
        sinopsis = request.form.get("sinopsis")

        if novel != "" and author != "":
            checks = db.execute("SELECT N.author_id FROM novels N JOIN authors A ON A.id = N.author_id WHERE A.name = ?", author)
            if len(checks) < 1:
                db.execute("INSERT INTO authors (name) VALUES (?)", author)
            checks = db.execute("SELECT author_id FROM novels WHERE title = ?", novel)
            if len(checks) < 1:
                author_id = db.execute("SELECT id FROM authors WHERE name = ?", author)
                author_id = author_id[0]["id"]
                db.execute("INSERT INTO novels (title, author_id, chapter_count, sinopsis, status) VALUES (?, ?, ?, ?, ?)", novel, author_id, 0, sinopsis, "active")
                return redirect(f"/read/{novel}")
            return error("Novel already exists", 400)
    else:
        return render_template("new_novel.html")


@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    info = db.execute("SELECT username, gender, about FROM users WHERE id = ?", user_id)
    info = info[0]
    pic = db.execute("SELECT picture FROM users WHERE id = ?", user_id)

    if len(pic) > 0:
        pic = pic[0]["picture"]
        pic = Image.open(BytesIO(pic))
        pic = pic.save("static/pic.jpg")
        pic = "static/pic.jpg"
        return render_template("profile.html", pic=pic, info=info)
    return render_template("profile.html", info=info)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        username = request.form.get("username")
        gender = request.form.get("gender")
        about = request.form.get("about")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 0:
            return error("Username already exists", 400)
        if "pic" not in request.files:
            return error("No file part", 400)
        items = {"username": username, "gender": gender, "about": about}

        for item in items:
            if items[f"{item}"] != "":
                db.execute(f'UPDATE users SET {item} = \'{items[f"{item}"]}\' WHERE id = ?', session["user_id"])
        pic = request.files["pic"]
        if pic.filename != "":
            pic = pic.read()
            db.execute("UPDATE users SET picture = ? AND username = ? AND gender = ? AND about = ? WHERE id = ?", pic, username, gender, about, session["user_id"])

        return redirect("/profile")
    else:
        return render_template("edit_profile.html")
