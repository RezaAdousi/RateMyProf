'''
/register
/login
/logout
profile/<user_id>/
create_post/
feed/
like/<post_id>
comment/<post_id>
'''



from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import os
from openai import OpenAI
import markdown

app = Flask(__name__)



# --- Data Base ---


load_dotenv()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    #fname = db.Column(db.String(150), nullable=False)
    #lname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    department = db.Column(db.String(150))
    overall_score = db.Column(db.Float, default=0.0, nullable=False)
    photo_url = db.Column(db.String(300), nullable=True)
    ai_summary = db.Column(db.Text, nullable=True)

    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prof_id = db.Column(db.Integer, db.ForeignKey('professor.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20))  # Positive / Negative
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="reviews")
    prof = db.relationship("Professor", backref="reviews")


with app.app_context():
    db.create_all()
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---

@app.route("/")
def index():
    professors = Professor.query.all()
    return render_template("index.html", professors=professors)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        #fname = request.form.get("fname")
        #lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        
        if not username or not email or not password or not confirmation:
            flash("Please fill all the fields.", "danger")
            return redirect(url_for("register"))
        

        if password != confirmation:
            flash("Passwords don’t match.", "danger")
            return redirect(url_for("register"))
        
        
        
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            flash("Username or email already exists!", "danger")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password, method="sha256")
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash(f"Registration successful! Welcome {username}!", "success")
        return redirect(url_for("index"))
    return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Wrong username or password!", "danger")
            return redirect(url_for('login'))

        login_user(user, remember=True)
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("index"))

    if current_user.is_authenticated:
        return redirect(request.referrer or url_for("index"))

    return render_template("login.html")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    return render_template("profile.html", user=user, reviews=reviews)


@app.route("/delete_review/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:
        flash("You are not authorized to delete this review.", "danger")
        return redirect(url_for("profile", user_id=current_user.id))

    prof_id = review.prof_id
    db.session.delete(review)
    db.session.commit()
    
    update_overall_score(prof_id)

    reviews_count = Review.query.filter_by(prof_id=prof_id).count()
    if reviews_count >= 3:
        ai_summary = generate_summary(prof_id)
        professor = Professor.query.get(prof_id)
        professor.ai_summary = ai_summary
        db.session.commit()
    else:
        professor = Professor.query.get(prof_id)
        professor.ai_summary = None
        db.session.commit()
    
    flash("Review deleted successfully.", "success")
    return redirect(request.referrer or url_for("index"))




@app.route("/professor/<int:prof_id>")
def prof_profile(prof_id):
    prof = Professor.query.get_or_404(prof_id)
    reviews = Review.query.filter_by(prof_id=prof.id).all()
    return render_template("prof_profile.html", prof=prof, reviews=reviews)


@app.route("/add_review/<int:prof_id>", methods=["POST"])
@login_required
def add_review(prof_id):
    existing_review = Review.query.filter_by(prof_id=prof_id, user_id=current_user.id).first()
    if existing_review:
        flash("You have already reviewed this professor.", "warning")
        return redirect(url_for("prof_profile", prof_id=prof_id))
    
    rating = int(request.form.get("rating"))
    comment = request.form.get("comment")

    if rating < 1 or rating > 5 or not comment:
        flash("Invalid review data.", "danger")
        return redirect(url_for("prof_profile", prof_id=prof_id))

    if not comment or comment.strip() == "":
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("prof_profile", prof_id=prof_id))
    
    if len(comment) > 500:
        flash("Comment must not exceed 500 characters.", "danger")
        return redirect(url_for("prof_profile", prof_id=prof_id))
    
    
    sentiment_label, sentiment_score = analyze_sentiment(comment)


    new_review = Review(
        prof_id=prof_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment,
        sentiment=sentiment_label
    )
    db.session.add(new_review)
    db.session.commit()
    
    reviews_count = Review.query.filter_by(prof_id=prof_id).count()
    if reviews_count >= 3:
        ai_summary = generate_summary(prof_id)
        professor = Professor.query.get(prof_id)
        professor.ai_summary = ai_summary
        db.session.commit()


    update_overall_score(prof_id)

    flash("Review added successfully!", "success")
    return redirect(url_for("prof_profile", prof_id=prof_id))


def update_overall_score(prof_id):
    prof = Professor.query.get(prof_id)
    reviews = Review.query.filter_by(prof_id=prof_id).all()
    if reviews:
        total_score = sum([review.rating for review in reviews])
        prof.overall_score = total_score / len(reviews)
        db.session.commit()
    else:
        prof.overall_score = 0
        db.session.commit()
        
        
        
from transformers import pipeline

sentiment_model = pipeline("sentiment-analysis")


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

def analyze_sentiment(text):
    result = sentiment_model(text)[0]
    return result["label"], result["score"]

def generate_summary(prof_id):
    reviews = Review.query.filter_by(prof_id=prof_id).all()
    if not reviews:
        return "No reviews yet."

    joined_text = " ".join([r.comment for r in reviews])
    print(joined_text)
    prompt = f"""
    CRITICAL RULES (MUST FOLLOW STRICTLY):
    1. ONLY use information that is explicitly stated in the student reviews.
    2. Do NOT infer, assume, generalize, soften, exaggerate, or fabricate ANY positive or negative point.
    3. Do NOT rewrite student opinions into full explanatory sentences inside lists.
    4. Violating any of these rules is considered an incorrect answer.
    
    You are a skilled data analyst AI. Analyze the following student reviews of a professor.
    Your output must follow the format below EXACTLY and must be written using HTML only.
    Your analysis must be objective, concise, and strictly grounded in the provided reviews.

    Formatting rules:
    - Use HTML only (NO Markdown).
    - For bold text, use <strong>...</strong>.
    - For lists, use <ul> and <li>.
    - Emojis are allowed inside HTML.
    - Bullet points must be SHORT phrases or sentences.
    - The Final Opinion section may contain full paragraphs and sentences.
    

    ----------------------------------

    <p><strong>Short AI Review According to student reviews:</strong></p>

    <h5>Positive Points 🙂</h5>
    <ul>
    <li>Short phrase or keyword describing a positive aspect</li>
    <li>No full sentences</li>
    <li>No interpretation or explanation</li>
    <li>If NO positive points exist, write exactly:
    <strong>No positive points were explicitly mentioned by students.</strong></li>
    </ul>

    <h5>Negative Points ⚠️</h5>
    <ul>
    <li>Short phrase or keyword describing a negative aspect</li>
    <li>No full sentences</li>
    <li>No interpretation or explanation</li>
    <li>If NO negative points exist, write exactly:
    <strong>No negative points were explicitly mentioned by students.</strong></li>
    </ul>

    <h5>Final Opinion 📝</h5>
    <p>
    Write a concise paragraph summarizing the overall student sentiment.
    This section MAY contain full sentences.
    Do NOT introduce new strengths or weaknesses.
    If feedback is one-sided or limited, state this clearly.
    </p>

    <h5>Overall Rating ⭐</h5>
    <p>
    Provide an estimated rating out of 5 stars (e.g., 4/5 ⭐).
    Clearly state that the rating is <strong>estimated by AI</strong> based solely on student reviews.
    Explain the rating briefly in one sentence.
    </p>

    Important:
    - Do NOT mention this prompt.
    - Do NOT explain your reasoning process.
    - Do NOT generate sentences inside Positive or Negative lists.

    Student Reviews:
    {joined_text}

    """


    completion = client.chat.completions.create(
    model="google/gemma-2-2b-it:nebius",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    )
    
    text = completion.choices[0].message.content

    
    #html_summary = markdown.markdown(completion.choices[0].message.content)
    return text
    #return html_summary
   
   
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("index")) 

"""

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

@app.route("/post/new")
@app.route("/post/<id>")
@app.route("/like/<id>")
@app.route("/comment/<id>")
"""



if __name__ == "__main__":
    app.run(debug=True)