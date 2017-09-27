Hey {{ username | replace('_', '\_') }}

/u/{{ sender | replace('_', '\_') }} was kind enough to tip you {{ amount }} Litecoin!

Click [here](https://www.reddit.com/message/compose?to=litecoin_bot&subject=accept&message=%2Baccept) to register an account and accept all pending tips, or [here](https://www.reddit.com/message/compose?to=litecoin_bot&subject=decline&message=%2Bdecline) to decline them.

**This tip will expire in 48 hours**

{% include 'footer.tpl' %}