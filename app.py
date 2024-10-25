from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
import stripe
from dotenv import load_dotenv
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load environment variables from .env file
load_dotenv()

# Stripe API keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Initialize SQLite DB (for users)
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        conn.commit()

init_db()

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            if user:
                session['user'] = user[1]
                return redirect(url_for('index'))
            else:
                flash('Login failed. Please check your credentials.')
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        flash('Account created! You can now log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Home route (certificate customization)
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process the form and handle Stripe payment
        name = request.form['name']
        course = request.form['course']
        stripe_token = request.form['stripeToken']
        template = request.files['template']

        try:
            # Charge the card
            stripe.Charge.create(
                amount=500,  # Charge $5.00
                currency='usd',
                description=f'Payment for {name} - {course}',
                source=stripe_token
            )

            # Generate certificate
            certificate_image = generate_certificate(name, course, template)
            return send_file(certificate_image, mimetype='image/png', as_attachment=True, download_name='certificate.png')

        except stripe.error.StripeError as e:
            flash(f"Payment error: {e.user_message}")

    return render_template('index.html', key=publishable_key)

def generate_certificate(name, course, template):
    # Load the template image uploaded by the user
    image = Image.open(template)
    draw = ImageDraw.Draw(image)

    from PIL import ImageFont

    # Path to the font file (make sure it points to the actual location of the font)
    font_path = "/storage/emulated/0/arial.ttf"

    # Define the font size
    font = ImageFont.truetype(font_path, size=40)

    # Add text (e.g., center-align the name and course)
    draw.text((150, 200), f'{name}', font=font, fill='black')  # Adjust positions accordingly
    draw.text((150, 300), f'{course}', font=font, fill='black')

    # Save to a BytesIO object for sending via Flask
    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

if __name__ == '__main__':
    app.run(debug=True)
