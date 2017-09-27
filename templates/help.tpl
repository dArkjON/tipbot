Welcome {{ username | replace('_', '\_') }}! This message is meant to be a quick introduction to /u/litecoin_bot.

###What is litecoin_bot?
litecoin_bot is an automated program written to help Redditors send Litecoin to other users on Reddit.  If you ever wanted to reward someone with more than upvotes and Reddit Gold now you can!

###OK cool, how does it work?

You can get started with these 3 easy steps:

1. Register with litecoin_bot by sending a [+register](https://www.reddit.com/message/compose?to=litecoin_bot&subject=register&message=%2Bregister) message
2. Acquire some Litecoins using a cryptocurrency exchange
3. Deposit the coins into the lprovided address and use them for tipping!

After you have the coins in your litecoin_bot account, tipping is as simple as leaving this in your comment:

    +/u/litecoin_bot tip 0.5

^(Tip the comment you're replying to 0.5 LTC)

###Commands

[+info](https://www.reddit.com/message/compose?to=litecoin_bot&subject=info&message=%2Binfo): get information about your account: Litecoin address and balance.

[+register](https://www.reddit.com/message/compose?to=litecoin_bot&subject=register&message=%2Bregister): create an account. The bot will generate a unique Litecoin address, and send you that info.

[+withdraw](https://www.reddit.com/message/compose?to=litecoin_bot&subject=withdraw&message=%2Bwithdraw%20ADDRESS%20AMOUNT%20TYPE): tell the bot to send Litecoin to a given address. Some examples of its syntax are:

    +withdraw ADDRESS 0.5 LTC

    +withdraw ADDRESS 3.50 USD (Currently supports USD, CAD, EUR, GBP, JPY, and RUB)

    +withdraw ADDRESS all

> ***Note***: *Network transaction fees are automatically added when tipping and withdrawing funds. For example, if you ask to withdraw 1 Litecoin, your total withdraw amount will be 1.001 Litecoin, out of which 0.001 Litecoin will go towards the transaction fee. litecoin_bot bot does not keep transaction fees - they go to the miners as a payment for processing the transaction*.

[+accept](https://www.reddit.com/message/compose?to=litecoin_bot&subject=accept&message=%2Baccept): accept all pending tips. If you've received a tip before you've registered with litecoin_bot, it's marked as pending until you +accept or +decline it. Pending tips expire in 48 hours.

[+decline](https://www.reddit.com/message/compose?to=litecoin_bot&subject=decline&message=%2Bdecline): decline all pending tips. If you've received a tip before you've registered with litecoin_bot, it's marked as pending until you +accept or +decline it. Pending tips expire in 48 hours.

###Tipping

+/u/litecoin_bot tip: The main command, used to tip other users. The basic syntax is:

    +/u/litecoin_bot tip [AMOUNT]

    +/u/litecoin_bot tip 0.1

^(Tip the author of the parent comment 0.1 LTC.)

In addition to specifying amount of Litecoin to tip, you could also specify a currency - USD, CAD, Euro, etc. litecoin_bot will automatically convert the currency value into its LTC value according to the exchange rate on [coinmarketcap.com](https://coinmarketcap.com/). The syntax is:

    +/u/litecoin_bot tip [AMOUNT] [USD|CAD|EUR|GBP|JPY|RUB|LTC|LITECOIN]

    +/u/litecoin_bot tip 500.00 jpy

*If you do not specify a currency the default value is LTC*

###Verification Messages

####Successful tips:

litecoin_bot will verify successful tips by replying to the +/u/litecoin_bot tip comment (except where banned). Here's an example of verification reply:

>***[VERIFIED]*** */u/not_a_hippie >>> /u/zeddstark 1.0 LTC*

####Unsuccessful tips:

In case the +/u/litecoin_bot tip command doesn't go through, litecoin_bot will not reply to the tip comment. It will send a personal message to the author of the tip command with a notice of what went wrong.

####Tips to unregistered users:

In case you tip a user who's not yet registered with litecoin_bot, your tip becomes 'pending' until the user decides to +accept or +decline it, or the tip expires.Pending tips are substracted from your balance and are credited back when declined or expired. Pending tips will expire in 48 hours.

When a pending tip is accepted, litecoin_bot will verify it as successful and reply to the +/u/litecoin_bot tip comment with the verification message like above.

###Balances

Your balance can be seen with the [+info](https://www.reddit.com/message/compose?to=litecoin_bot&subject=info&message=%2Binfo) command. Notice that after depositing LTC to the addresses provided or sending a tip, there's a delay before the new balance becomes available for tipping. 

###Staying Safe
This service is in early BETA. You are using this service at your own risk. In addition, the coins in your account are only as secure as your Reddit account. Please adhere to the following safety guidlines:

- Do not deposit any serious amounts of Litecoin
- Withdraw any Litecoin you don't use for tipping
- Make sure your Reddit account is secure
- Make sure the computer you're using is secure

^(litecoin_bot was created by /u/not_a_hippie.)
^(Feel free to send a pm with any questions/concerns/suggestions.)

^(Donations are cool: LbHb4Qn6xUzEXWcTTw7SjS3YDs2Hw6sXpi)



