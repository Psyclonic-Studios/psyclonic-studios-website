const checkoutButton = document.getElementById("checkout-button");

function addToQuantity(sku, amount, hasDisplay = true) {
  const product = products[sku];
  product.quantity += amount;
  if (product.quantity < 0) product.quantity = 0;
  if (hasDisplay) updateQuantityDisplay(sku);
  updateCost();
}

function updateQuantityDisplay(sku) {
  const productQuantityDisplay = document.getElementById(sku);
  productQuantityDisplay.textContent = products[sku].quantity;
}

function updateCost() {
    let totalCost = 0;
    for(let [sku, product] of Object.entries(products)) {
      totalCost += product.quantity * product.price;
    }
    checkoutButton.textContent = "Checkout " + totalCost.toLocaleString('en-AU', {currency: 'AUD', currencyDisplay: 'symbol', style: 'currency'});
}

(function() {
  var stripe = Stripe('pk_test_54LxtB4vZjsleKrRO5zqpuV1');

  var checkoutButton = document.getElementById('checkout-button');
  checkoutButton.addEventListener('click', function () {
    stripe.redirectToCheckout({
      items: Object.keys(products).filter(sku => products[sku].quantity > 0).map(sku => { return {sku: sku, quantity: products[sku].quantity} }),
      successUrl: 'https://www.psyclonicstudios.com.au/success',
      cancelUrl: 'https://www.psyclonicstudios.com.au/canceled',
    })
    .then(function (result) {
      if (result.error) {
        var displayError = document.getElementById('error-message');
        displayError.textContent = result.error.message;
      }
    });
  });
})();