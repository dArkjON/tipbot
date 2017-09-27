Hello {{ username | replace('_', '\_') }}! Here's your account info:

Address|Balance
:--|:--
{{ address }} | {{ balance }} LTC {% if pending != 0 %}*({{ pending }} LTC pending)*{% endif %}

{% if balance is equalto "0" %}

**FAQ**

**Q: How do I get litecoin?**

A: One of the easiest ways to get Litecoin is through [https://www.coinbase.com](https://www.coinbase.com/).  Once you have Litecoin simply send them to your address above to start tipping!

**Q: I should have Litecoin. Why is my balance 0?**

A: If you just sent Litecoin to your account or if you just sent a tip, your balance will show 0 until the transaction is confirmed by the network.  This may take a few minutes. Don't worry your litecoin will be available soon.
{% endif %}

{% include 'footer.tpl' %}