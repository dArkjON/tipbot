Hey {{ username | replace('_', '\_') }} our records show that you do not have enough funds to withdraw the amount you requested.

Requested withdrawal: `{{ amount }} LTC`

Available balance: `{{ balance }} LTC`

{% if balance is equalto "0" %}
**FAQ**

**Q: I should have Litecoin. Why is my balance 0?**

A: If you just sent Litecoin to your account or if you just sent a tip, your balance will show 0 until the transaction is confirmed by the network.  This may take a few minutes. Don't worry your litecoin will be available soon.
{% endif %}

{% include 'footer.tpl' %}