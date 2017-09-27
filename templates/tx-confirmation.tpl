Hello {{ username | replace('_', '\_') }},

You just sent {{ amount }} LTC to {{ address }}

Transaction id: {{ txid }}

{% include 'footer.tpl' %}