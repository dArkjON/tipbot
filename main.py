# -*- coding: utf-8 -*-
import logging
import re
import time
from requests.exceptions import HTTPError, ConnectionError, Timeout

import praw
import yaml

import tipbot_action
from misc import checksum, price

# logging configuration
logging.basicConfig(filename="logs/tipbot.log", 
    format="%(asctime)s %(levelname)s: %(message)s", 
    datefmt='%m/%d/%Y %I:%M:%S %p', 
    level=logging.INFO)


class TipBot(object):

    def __init__(self):
        ymlfile = open('config/config.yml', 'r')
        cfg = yaml.load(ymlfile)
        self.username = cfg['reddit']['username']
        self.password = cfg['reddit']['password']
        self.client_id = cfg['reddit']['client_id']
        self.client_secret = cfg['reddit']['client_secret']
        self.user_agent = cfg['reddit']['user_agent']
    
    # acceptable fiat currencies
    fiat = {"usd", "cad", "eur", "gbp", "jpy", "rub"}
    
    def login(self):

        try:
            self.reddit = praw.Reddit(client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password)
            logging.info("TipBot::login(): Login sucessful")
            return True
        except:
            logging.error("TipBot::login(): Error logging in")
            return False

    def parse_message(self, message):
        """
        parse an inbox message for a command. if a command
        is found, execute the command. if no command is found
        or if the syntax is invalid let the sender know
        """

        user = str(message.author)
        body = message.body
        
        rg = re.compile("^(\+accept|\+decline|\+help|\+info|\+register)$|^(\+withdraw)", re.IGNORECASE)
        match = rg.search(body)

        if match:

            logging.info("TipBot::parse_message(): message from {}".format(user))
            
            command = match.group(0).lower()
            if command == "+info":
                tipbot_action.info(self.reddit, user)
            elif command == "+register":
                tipbot_action.register(self.reddit, user)
            elif command == "+help":
                tipbot_action.help(self.reddit, user)
            elif command == "+accept":
                tipbot_action.accept(self.reddit, user)
            elif command == "+decline":
                tipbot_action.decline(self.reddit, user)
            elif command == "+withdraw":
                try:
                    rg = re.compile("^(\+withdraw)(\s+)([a-zA-Z0-9]{34})(\s+)([0-9]{1,9}(?:\.[0-9]{0,8})?|all)(?:\s+(ltc|litecoin|usd|cad|gbp|eur|rub))?", re.IGNORECASE)
                    m = rg.search(body)

                    address = m.group(3)

                    # make sure the litecoin address is valid
                    if not checksum.validate_address(address):
                        err_msg = "invalid litecoin address. double check for typos."
                        tipbot_action.error(self.reddit, user, err_msg)
                        return

                    amount = m.group(5)
                    c_type = m.group(6) # litecoin/usd/cad/etc..
                except:
                    err_msg = "invalid message syntax"
                    tipbot_action.error(self.reddit, user, err_msg)
                    logging.info("TipBot::parse_message(): syntax error")
                    return

                if amount.lower() == "all":
                    tipbot_action.withdraw_all(self.reddit, user, address)
                elif c_type.lower() in self.fiat:
                    # convert fiat to ltc value
                    ltc_amount = price.convert_to_ltc(float(amount), c_type)
                    tipbot_action.withdraw(self.reddit, user, address, ltc_amount)
                else:
                    tipbot_action.withdraw(self.reddit, user, address, float(amount))
        # ignore
        else:
            logging.info("TipBot::parse_message(): message from {}...no match".format(user))
            err_msg = "invalid message syntax"
            tipbot_action.error(self.reddit, user, err_msg)

    def parse_comment(self, comment):
        """
        parse comments/mentions for tip commands. if a command
        is found, execute the command. if no command is found
        or if the syntax is invalid let the sender know
        """
        
        user = str(comment.author)
        body = comment.body

        rg = re.compile("(\+/u/litecoin_bot)(\s+)(tip)(\s+)([0-9]{1,9}(?:\.[0-9]{0,8})?)(?:\s+(ltc|litecoin|usd|cad|gbp|eur|rub))?", re.IGNORECASE)
        match = rg.search(body)
        
        if not match:
            # could not match regex, ignore
            logging.info("TipBot::parse_comment(): comment from {}...no match".format(user))
            err_msg = "invalid comment syntax"
            tipbot_action.error(self.reddit, user, err_msg)
            return

        logging.info("TipBot::parse_comment(): comment from {}".format(user))
        
        # get author of parent submission/comment
        parent_id = comment.parent()
        if comment.is_root:
            parent_info = self.reddit.submission(id=parent_id)
            parent_author = parent_info.author
        else:
            parent_info = self.reddit.comment(id=parent_id)
            parent_author = parent_info.author   
        # convert praw object to string
        parent_author = str(parent_author)
            
        if user == parent_author:
            # user tipped themself, ignore
            logging.info("TipBot::parse_comment(): {} tryed to tip themself".format(user))
            err_msg = "user can't tip themself"
            tipbot_action.error(self.reddit, user, err_msg)
            return 

        if parent_author == self.username:
            # user tipped bot, ignore
            logging.info("TipBot::parse_comment(): {} tryed to tip themself".format(user))
            err_msg = "thanks, but I don't accept tips"
            tipbot_action.error(self.reddit, user, err_msg)
            return 

        # get amount and currency type from regex
        amount = match.group(5)
        c_type = match.group(6)
            
        if c_type.lower() in self.fiat:
            # convert fiat to ltc value
            ltc_amount = price.convert_to_ltc(float(amount), c_type)
            tipbot_action.tip(self.reddit, user, parent_author, ltc_amount, comment)
        else:
            tipbot_action.tip(self.reddit, user, parent_author, float(amount), comment)

    def check_inbox(self):
        """
        check the inbox for any new messages/comments
        """

        logging.debug('TipBot::check_inbox()')

        try:
            # try to fetch some messages
            messages = list(self.reddit.inbox.unread(limit=1000))
            messages.reverse() # we want to evaluate the oldest messages first

            # process messages
            for m in messages:
                # sometimes messages don't have an author
                if not m.author:
                    logging.info("TipBot::check_inbox(): ignoring message with no author")
                    m.mark_read()
                    continue
                # ignore self messages
                if m.author and m.author.name.lower() == '/u/' + self.username.lower():
                    logging.debug("TipBot::check_inbox(): ignoring message from self")
                    m.mark_read()
                    continue

                action = None
                if m.was_comment:
                    # attempt to evaluate as comment / mention
                    action = self.parse_comment(m)
                else:
                    # attempt to evaluate as inbox message
                    action = self.parse_message(m)

                # perform action, if found
                if action is not None:
                    action.do()

                m.mark_read()
        
        except (HTTPError, ConnectionError, Timeout) as e:
            logging.warning("TipBot::check_inbox(): Reddit is down ({}), sleeping".format(e))
            time.sleep(60)
            pass

        except Exception as e:
            logging.error("TipBot::check_inbox():".format(e))
            raise

        logging.debug("TipBot::check_inbox() DONE")
        return True

    def start(self):
        self.login()
        print("*** {} running ***".format(self.username))
        while True:
            self.check_inbox()
            tipbot_action.expire_pending_tips()
            time.sleep(60)

litecoin_bot = TipBot()
litecoin_bot.start()