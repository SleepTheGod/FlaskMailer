from flask import Flask, request, render_template, redirect, url_for, flash
import os
import time
import requests
from contextlib import contextmanager
from requests.exceptions import RequestException

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Set your secret key for session management

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to send Mailgun email
def send_mailgun_email(domain, api_key, sender, recipient, subject, html_body):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": sender,
            "to": recipient,
            "subject": subject,
            "html": html_body
        }
    )

@contextmanager
def timeout(duration):
    """A context manager to enforce a time limit for code execution."""
    try:
        yield
    except Exception as e:
        print(f"Error: {e}")
        raise TimeoutError(f"Execution exceeded {duration} seconds.")

# Flask route to handle file uploads
@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # Save uploaded files
        subject_file = request.files['subject_file']
        body_file = request.files['body_file']
        recipients_file = request.files['recipients_file']
        
        # Save the files to the upload folder
        subject_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'subject.txt'))
        body_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'body.html'))
        recipients_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'recipients.txt'))
        
        flash('Files uploaded successfully. Sending emails...', 'success')
        return redirect(url_for('send_emails'))

    return render_template('upload.html')

# Flask route to send emails
@app.route('/send', methods=['GET'])
def send_emails():
    try:
        # Load subject and body from uploaded files
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'subject.txt'), 'r') as file:
            subject = file.read().strip()

        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'body.html'), 'r') as file:
            body_html = file.read().strip()

        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'recipients.txt'), 'r') as file:
            recipients = [line.strip() for line in file if line.strip()]

    except FileNotFoundError as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('upload_files'))

    # Initialize Mailgun
    domain = "your-mailgun-domain.com"
    api_key = "your-api-key-here"
    sender = "you@yourdomain.com"

    # Email sending process
    sent_count = 0
    start_time = time.time()

    for recipient in recipients:
        try:
            with timeout(10):
                response = send_mailgun_email(domain, api_key, sender, recipient, subject, body_html)

                if response.status_code == 200:
                    sent_count += 1
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] Sent to: {recipient} | Total sent: {sent_count}")
                else:
                    print(f"Failed to send to {recipient}: {response.status_code} - {response.text}")

        except TimeoutError:
            print(f"Failed to send to {recipient}: Timeout error")
        except RequestException as e:
            print(f"Failed to send to {recipient}: {str(e)}")

        time.sleep(2.1)  # Sleep between emails

    elapsed_time = time.time() - start_time
    flash(f"Finished sending emails. Total sent: {sent_count}. Time elapsed: {elapsed_time:.2f} seconds.", 'info')

    return render_template('result.html', sent_count=sent_count, elapsed_time=elapsed_time)

if __name__ == "__main__":
    app.run(debug=True)
