
from flask import(
    Blueprint, render_template, request, flash, redirect, url_for,current_app
)

import sendgrid
from sendgrid.helpers.mail import *

from app.db import get_db



bp = Blueprint('mail', __name__, url_prefix="/")

@bp.route("/", methods=["GET"])
def index():
    search = request.args.get('search')
    db, c = get_db()
    if search is not None:
        c.execute("SELECT * FROM email WHERE content LIKE %s", ('%' + search+ '%',))    
    else:
        c.execute("SELECT * FROM email")
    mails =c.fetchall()
    
    return render_template('mails/index.html', mails = mails)

@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method=="POST":
        
        mail=request.form.get('email')
        subject=request.form.get('subject')
        content=request.form.get('content')
        errors =[]
        if not mail:
            errors.append('el correo es obligatorio')
        
        if not subject:
            errors.append('el asunto es obligatorio')
            
        if not content:
            errors.append('el contenido del correo esta vacio')
        if len(errors) == 0:
            send(mail,subject, content)
            db, c = get_db()
            c.execute("INSERT INTO email (email, subject, content) VALUES(%s, %s, %s)",(mail, subject, content))
            db.commit()

            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)
        
        



    return render_template('mails/create.html')

def send(to, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_KEY'])

    from_email = Email(current_app.config['FROM_EMAIL'])
    to_email = To(to)
    content = Content('text/plain',content)
    mail= Mail(from_email,to_email,subject, content)
    
    response = sg.send(mail)
    print(response)
    