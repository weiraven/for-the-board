from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

dummy_data = [
    {
        "id": 1,
        "title": "Dwarves are gey, lemme explain",
        "content": "I rest my case.",
        "author": "John Doe",
        "date_posted": "11/09/2023",
        "avatar": "https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg",
    },
    {
        "id": 2,
        "title": "Dwarves are not gey, don't lemme explain",
        "content": "I rest.",
        "author": "Doe John",
        "date_posted": "11/09/2023",
        "avatar": "https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg",
    },
]


@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html")


@app.get("/forum")
def forum():
    # Needs to display forum components from db
    return render_template("forum.html", posts=dummy_data)


@app.get("/forum/<int:forum_id>")
def get_single_forum(forum_id: int):
    # brings a new page that display specific forum post
    forum_post = dummy_data[forum_id]
    return render_template("get_single_forum.html", forum=forum_post)


@app.post("/submit_post")
def submit_forum_post():
    # after post, redirect back to forum.html. maybe redirect to this post new page (get_single_forum)
    title = request.form["title"]
    content = request.form["content"]
    author = request.form["author"]
    date_posted = "11/09/2023"
    avatar = "https://i.kym-cdn.com/entries/icons/facebook/000/014/711/neckbeard.jpg"
    id = int(len(dummy_data) + 1)
    dummy_data.append({id, title, content, author, date_posted, avatar})
    return redirect("/forum")


@app.post("/submit_comment")
def submit_forum_comment():
    # after post, redirect back to get_single_form.html
    return

    return render_template("forum.html")


@app.get("/createAccount")
def account():
    return render_template("account.html")
