# Litecoin Bot

A litecoin tipbot for Reddit. For an introduction and to see how the bot works, read [here](https://www.reddit.com/r/litecoinbot/wiki/index)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Python Dependencies

Python 3.5+

Lastest version of jinja2, praw, pyyaml, sqlalchemy:

```
pip3 install jinja2
pip3 install praw
pip3 install pyyaml
pip3 install sqlalchemy
```

### Database

To get the necessary sqlite tables run:

```
python3 tabledef.py
```

### Litecoin Daemon

You will need to run a litecoin daemon in order to create addresses/transactions.
For help and instructions see [here](https://github.com/bryan2048/tipbot/wiki/Installing-Litecoin).

### Configuration

You should create a dedicated Reddit account for your bot.  Open config/config.yml and fill out client_id, client_secret, username, and password with the information from your dedicated account.

### Running the Bot

1. Ensure the  Litecoin daemon is running and responding to commands.

2. Ensure you created the necessary tables.

3. Ensure Reddit authenticates configured user.

4. Execute ```python3 main.py```. The command will not return for as long as the bot is running.