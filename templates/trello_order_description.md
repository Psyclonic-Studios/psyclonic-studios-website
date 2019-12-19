## [See the order email here]({{ gmail_link }})

## Order details
{% for item in order.artworks %}
{% set artwork = item.artwork %}
{% set thumbnail_image = artwork.images | first %}
* {{ artwork.price | format_money }}: [{{ artwork.title }}]({{ url_for('artwork', id=artwork.id, _external=True) }})
{% endfor %}

## Cost
Product subtotal: {{ order.cost.subtotal | format_money }}
Shipping cost: {{ order.cost.shipping | format_money }}
Total: {{ order.cost.total | format_money }}

## Customer details
Name: {{ order.customer.name }}
Email address: {{ order.customer.email }}

## Shipping details
Street: {{ order.shipping.street }}
City: {{ order.shipping.city }}
State: {{ order.shipping.state }}
Country: {{ order.shipping.country }}
Postal code: {{ order.shipping.postal_code }}