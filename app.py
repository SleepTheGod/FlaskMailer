from flask import Flask, render_template, request, flash, redirect, url_for
from mailgun import Mailgun
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secure secret key for session management

# Initialize Mailgun API
MAILGUN_DOMAIN = "your-mailgun-domain.com"
MAILGUN_API_KEY = "your-mailgun-api-key"
mg = Mailgun(MAILGUN_DOMAIN, MAILGUN_API_KEY)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get files from the form
        subject_file = request.files.get('subject_file')
        body_file = request.files.get('body_file')
        recipients_file = request.files.get('recipients_file')

        if not subject_file or not body_file or not recipients_file:
            flash("Please upload all required files (subject.txt, body.html, recipients.txt).", "danger")
            return redirect(url_for('index'))

        # Read the uploaded files
        try:
            subject = subject_file.read().decode('utf-8').strip()
            body = body_file.read().decode('utf-8').strip()
            recipients = recipients_file.read().decode('utf-8').strip().splitlines()
        except Exception as e:
            flash(f"Error reading uploaded files: {e}", "danger")
            return redirect(url_for('index'))

        # Send emails
        sent_count, elapsed_time = send_emails(subject, body, recipients)

        # Display results
        flash(f"Successfully sent {sent_count} emails in {elapsed_time:.2f} seconds.", "success")
        return render_template('result.html', sent_count=sent_count, elapsed_time=elapsed_time)

    return render_template('index.html')


def send_emails(subject, body, recipients):
    start_time = time.time()
    sent_count = 0

    for email in recipients:
        email = email.strip()
        if not email:
            continue

        try:
            mg.send_email(
                from_email="you@yourdomain.com",
                to_email=email,
                subject=subject,
                html_body=body
            )
            sent_count += 1
        except Exception as e:
            flash(f"Failed to send to {email}: {e}", "danger")

        time.sleep(2.1)  # Sleep to avoid hitting rate limits (2.1 seconds between emails)

    elapsed_time = time.time() - start_time
    return sent_count, elapsed_time


if __name__ == '__main__':
    app.run(debug=True)
