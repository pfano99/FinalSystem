from flask import Blueprint,render_template, redirect, url_for, request, abort, flash
from flask_login import current_user, login_required
from Work.models import Farmer, Message, Restuarant
from Work.Messaging.forms import MessageForm
from Work import db
from datetime import datetime
from sqlalchemy import and_ 

chat = Blueprint('Chat', __name__)

def filter_chat_history(c_hist):
    usernames = []
    c = []
    for i in c_hist:
        if current_user.user_type == 1:
            if not i.farmer.username in usernames:
                usernames.append(i.farmer.username)
                c.append(i)
        else:
            if not i.restuarant.username in usernames:
                usernames.append(i.restuarant.username)
                c.append(i)

    return c

@chat.route('/farmer/chat/<int:recipient_id>', methods=['POST', 'GET'])
@login_required
def send_message(recipient_id):
    
    title = "Chat"
    form = MessageForm()
    
    message = None
    if current_user.user_type == 0:
        messages = Message.query.filter(and_(Message.farmer_id==current_user.id, Message.restuarant_id == recipient_id))
    else:
        messages = Message.query.filter(and_(Message.farmer_id==recipient_id, Message.restuarant_id == current_user.id))

    # Updating the latest time the current_user read thier message 
    current_user.last_read_time = datetime.utcnow()
    db.session.commit()

    if form.validate_on_submit():
        if current_user.user_type == 0:
            message = Message(
                farmer_id = current_user.id,
                restuarant_id = recipient_id,
                body = form.message.data,
                sender_type = current_user.user_type
            )
            db.session.add(message)
        else:
            message = Message(
                farmer_id = recipient_id,
                restuarant_id = current_user.id,
                body = form.message.data,
                sender_type = current_user.user_type
            )
            db.session.add(message)

        db.session.commit()

    return render_template('Messaging/messages.html',form=form, title = title, messages=messages)



@chat.route('/chats/')
@login_required
def chats_history():
    chats = None
    if current_user.user_type == 0:
        chats = Message.query.filter_by(farmer_id=current_user.id)
    else:
        chats = Message.query.filter_by(restuarant_id=current_user.id)

    title="Chats history"
    chats = filter_chat_history(chats)
    # print(chats)
    return render_template('Messaging/chat.html',chats=chats, title=title)





# @chat.route('/user/chat/messages/<string:recipient_username>', methods=['POST', 'GET'])
# @login_required
# def view_message(recipient_username):

#     recipient = User.query.filter_by(username=recipient_username).first_or_404()
#     title = "Messages"
#     current_user.last_read_time = datetime.utcnow()
#     db.session.commit()
#     messages = Message.query.filter( and_(Message.recipient_id == recipient.id, Message.sender_id == current_user.id)).union(
#         Message.query.filter( and_(Message.sender_id == recipient.id, Message.recipient_id == current_user.id))
#     ).order_by(Message.timestamp.asc() )    

#     return render_template("Messaging/messages.html", title=title, messages=messages )


