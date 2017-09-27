import logging
from datetime import datetime

import praw
import yaml
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from misc import pylitecoin
from tabledef import *

# litecoin daemon
ymlfile = open('config/config.yml', 'r')
cfg = yaml.load(ymlfile)
account = cfg["litecoind"]["account"]

# database stuff
engine = create_engine("sqlite:///litecoinbot.db", echo=False)
Session = sessionmaker(bind=engine)

# jinja 2
template_loader = FileSystemLoader(searchpath="./templates")
env = Environment(loader=template_loader)

# transaction fee and min for withdrawals
TX_FEE = 0.001
WITHDRAW_MIN = 0.01


def send_message(reddit, username, sub, msg):
    """
    send a message to a user on reddit

    :param reddit: a praw reddit instance
    :param userame: the redditors username
    :param sub: the subject of the message
    :param msg: the body of the message
    """
    logging.info("send_message(): message sent to {}".format(username))
    reddit.redditor(username).message(sub, msg)


def info(reddit, username):
    """
    if the user has already registered an account 
    send them information about their account

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    """
    if not user_exists(username):
        # user hasn't registered an account
        logging.info("info(): no info for {}".format(username))
        template = env.get_template('no-info.tpl')
        s = "No info"
        m = template.render(username=username) 
    else:
        logging.info("info(): getting info for {}".format(username))
        address = get_address(username)
        balance = str(pylitecoin.get_address_balance(address))
        pending = pending_tip_total(username)

        # send user a message with their information
        template = env.get_template('info.tpl')
        s = "Account Info"
        m = template.render(username=username, address=address, balance=balance, pending=pending)

    send_message(reddit, username, s, m)


def help(reddit, username):
    """
    Send user a help message with instructions on
    how to use the bot

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    """
    template = env.get_template('help.tpl')
    s = "Help"
    m = template.render(username=username)

    send_message(reddit, username, s, m)

def register(reddit, username):
    """
    If the user does not have an account with litecoin_bot
    create an account and send them the info

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    """
    # check if user already exists
    if user_exists(username):
        address = get_address(username)
        logging.info("register(): {} is already registered".format(username))
        template = env.get_template('already-registered.tpl')
        s = "Account already exists"
        m = template.render(username=username)
    else:
        logging.info("register(): registering {}".format(username))
        session = Session()
        
        # generate address for new user
        address = pylitecoin.get_new_address(account)
        
        # add user to db
        new_user = User(username, address)
        session.add(new_user)
        session.commit()
        
        # send user a confirmation message with their address
        template = env.get_template('register.tpl')
        s = "Registration Message"
        m = template.render(username=username, address=address)

    send_message(reddit, username, s, m)


def withdraw(reddit, username, to_address, amount):
    """
    withdraw litecoin from user's litecoin_bot
    account and send it to the given address

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    :param to_address: the litecoin address we will send the funds to
    :param amount: the amount of litecoin to send
    """
    if not user_exists(username):
        # user doesnt exist, ignore msg
        logging.info("withdraw(): {} user {} does not exists".format(username))
        return

    # get the user's registered address
    from_address = get_address(username)
    # check if the user has any pending tips
    pending = pending_tip_total(username)

    tx_total = amount + TX_FEE
    balance = pylitecoin.get_address_balance(from_address) - pending

    if tx_total > balance:
        # user doesn't have enough funds to withdraw the requested amount
        template = env.get_template('not-enough-funds.tpl')
        s = "Not Enough Funds"
        m = template.render(username=username, amount=amount, balance=balance)

    elif tx_total < WITHDRAW_MIN:
        # withdrawal amount is below the minimum
        template = env.get_template('withdraw-below-min.tpl')
        s = "Withdrawal Does Not Meet Minimum"
        m = template.render(username=username, wmin=WITHDRAW_MIN)

    else:
        # get the transaction id and process the tx
        txid = pylitecoin.withdraw_from_address(amount, TX_FEE, 
        from_address, to_address)

        # send transaction confirmation
        template = env.get_template('tx-confirmation.tpl')
        s = "Transaction Confirmation"
        m = template.render(username=username, amount=amount, address=to_address, txid=txid)
    
    send_message(reddit, username, s, m)


def withdraw_all(reddit, username, to_address):
    """
    withdraw ALL litecoin from user's litecoin_bot
    account and send it to the given address

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    :param to_address: the litecoin address we will send the funds to
    """   
    if not user_exists(username):
        # user doesnt exist, ignore msg
        logging.info("withdraw_all(): {} does not have an account".format(username))
        return

    from_address = get_address(username)
    
    # check if the user has any pending tips
    pending = pending_tip_total(username)

    # get the user's balance from the daemon and subtract any
    # pending tips and the transaction fee for this transaction
    balance = pylitecoin.get_address_balance(from_address) - pending - TX_FEE

    if balance >= WITHDRAW_MIN:
        txid = pylitecoin.withdraw_from_address(balance, TX_FEE, 
            from_address, to_address)

        # send transaction confirmation
        template = env.get_template('tx-confirmation.tpl')
        s = "Transaction Confirmation"
        m = template.render(username=username, amount=balance, address=to_address, txid=txid)

    else:
        # withdrawal amount is below the minimum
        template = env.get_template('withdraw-below-min.tpl')
        s = "Withdrawal Does Not Meet Minimum"
        m = template.render(username=username, wmin=WITHDRAW_MIN)

    send_message(reddit, username, s, m)


def accept(reddit, username):
    """
    check if a user has any pending tips, if they do
    register an account for the user and accept all tips

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    """
    logging.info("accept(): {} accepted all pending tips".format(username))
    session = Session()
    pending_tips = list(session.query(Tip).filter(Tip.recipient == username).filter(Tip.status == "PENDING"))
    
    if not pending_tips:
        # no pending tips for this user
        logging.info("accept(): {} has no pending tips".format(username))
        session.close()
        return

    # if user doesn't have account create one for them
    if not user_exists(username):
        register(reddit, username)

    address = get_address(username)

    for t in pending_tips:
        from_address = get_address(t.sender)
        amount = t.amount - TX_FEE # when we stored the pending tip in the db we added the tx_fee
        amount = round(amount, 8)
        tip_id = t.tip_id

        # send transaction and leave a reply to the 'tip comment'
        pylitecoin.withdraw_from_address(amount, TX_FEE, from_address, address)
        reddit.comment(t.comment_id).reply("***[VERIFIED]*** */u/{} >>> /u/{} {} LTC [[help]](https://www.reddit.com/message/compose?to=litecoin_bot&subject=help&message=%2Bhelp)*".format(t.sender, t.recipient, amount))
        logging.info("accept(): replied to comment {}".format(t.comment_id))
        # update the record 
        r = list(session.query(Tip).filter(Tip.tip_id == tip_id))
        r[0].status = "ACCEPTED"
        session.commit()

    session.close()


def decline(reddit, username):
    """
    check if a user has any pending tips,
    if they do decline all of the tips

    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    """
    logging.info("decline(): {} declined all pending tips".format(username))
    session = Session()
    pending_tips = list(session.query(Tip).filter(Tip.recipient == username).filter(Tip.status == "PENDING"))

    if not pending_tips:
        # no pending tips for this user
        logging.info("decline(): {} has no pending tips".format(username))
        session.close()
        return

    for t in pending_tips:
        # update the record
        t.status = "DECLINED"
        session.commit()

    session.close()

def tip(reddit, sender, recipient, amount, comment_id):
    """
    send litecoin from one user to another and store a record
    or the transaction in a db. if the recipient hasn't 
    already registered an account the tip is stored in the db
    as pending. if the tip is sucessful tip() will reply
    to the comment with a verification message

    :param reddit: a praw reddit instance
    :param sender: username of the redditor sending the tip
    :param recipient: username of the redditor receiving the tip
    :param amount: value of the tip (in LTC)
    :param comment_id: id of the '+/u/litecoin_bot' tip comment
    """
    # sender doesn't have an account, ignore comment
    if not user_exists(sender):
        logging.info("tip(): user {} does not have an account".format(sender))
        return

    # make sure the sender has enough funds 
    # and the tip meets the minimum amount
    if not valid_tip_amount(sender, amount):
        logging.info("tip(): invalid tip amount")
        template = env.get_template('tip-went-wrong.tpl')
        s = "Uh-oh"
        m =template.render()
        send_message(reddit, sender, s, m)
        return

    if user_exists(recipient):
        logging.info("tip(): {} sent tip to {} [ACCEPTED]".format(sender, recipient))
        # get sender and recipients address'
        from_address = get_address(sender)
        to_address = get_address(recipient)

        # user already has an account so we mark tip as
        # accepted and create the transaction
        status = "ACCEPTED"
        pylitecoin.withdraw_from_address(amount, TX_FEE, from_address, to_address)
        reddit.comment(comment_id).reply("***[VERIFIED]*** */u/{} >>> /u/{} {} LTC [[help]](https://www.reddit.com/message/compose?to=litecoin_bot&subject=help&message=%2Bhelp)*".format(sender, recipient, amount))
    else:
        # recipient hasn't registered an accout yet
        # mark tip as pending and msg them with instructions
        # on how to claim the tip
        status = "PENDING"

        # when we store a pending tip in the db we also
        # have to add the pending transaction fee so that
        # it isn't spent
        amount += TX_FEE
        amount = round(amount, 8)

        logging.info("tip(): {} sent tip to {} [PENDING]".format(sender, recipient))
        template = env.get_template('yougottip.tpl')
        s = "You just got a tip!"
        m =template.render(username=recipient, sender=sender, amount=amount - 0.001)
        send_message(reddit, recipient, s, m)

    # add tip to db
    session = Session()
    tip = Tip(sender, recipient, round(amount, 8), status, str(comment_id))
    session.add(tip)
    session.commit()
    

def valid_tip_amount(username, amount):
    """
    return true if sender has enough funds 
    and the tip meets the minimum amount

    :param username: redditor's username
    :param amount: amount the user wants to tip
    """
    address = get_address(username)
    # check if the user has any pending tips
    pending = pending_tip_total(username)

    # subtract pending tips from user's balance
    balance = pylitecoin.get_address_balance(address) - pending
    tx_total = amount + TX_FEE

    if tx_total > balance:
        return False
    elif tx_total < WITHDRAW_MIN:
        return False
    else:
        return True


def pending_tip_total(username):
    """
    return the sum of the user's pending tips

    :param username: redditor's username
    """
    session = Session()
    total = 0.0
    
    tips = list(session.query(Tip).filter(Tip.sender == username))
    
    if not tip:
        # user has no pending tips
        session.close()
        return total
    else:
        for t in tips:
            if t.status == "PENDING":
                total += t.amount
        session.close()
        return round(total, 8)


def expire_pending_tips():
    """
    query the database and expire tips that
    have been pending for more than 48 hours
    """
    session = Session()
    now = datetime.now()
    pending_tips = list(session.query(Tip).filter(Tip.status == "PENDING"))

    if not pending_tips:
        # there are no pending tips
        logging.debug("expire_pending_tips(): no pending tips")
        session.close()
        return
    count = 0
    for t in pending_tips:
        if (now - t.time_sent).days >= 2:
            t.status = "EXPIRED"
            count += 1
            session.commit()
    if count > 0:
        logging.info("expire_pending_tips(): expired {} tips".format(count))
    session.close()


def error(reddit, username, e):
    """
    let user know there was an error parsing their inbox message/comment
    
    :param reddit: a praw reddit instance
    :param username: the user's username on reddit
    :param e: error message for the error template
    """
    template = env.get_template('error.tpl')
    s = "What?"
    m = template.render(err=e)
    
    send_message(reddit, username, s, m)


def user_exists(username):
    """
    if the user has an account return true, else return false

    :param username: redditor's username
    """
    session = Session()
    user = list(session.query(User).filter(User.username == username))
    if not user:
        session.close()
        return False
    else:
        session.close()
        return True


def get_address(username):
    """
    query the database and return the user's address

    :param username: redditor's username
    """
    session = Session()
    for user in session.query(User).filter(User.username == username):
        address = user.address
    session.close()
    
    return address
