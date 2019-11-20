const costElement = document.getElementById("cost")

function addToQuantity(sku, amount) {
  const product = products[sku];
  product.quantity += amount;
  if (product.quantity < 0) product.quantity = 0;
  const productQuantityDisplay = document.getElementById(sku);
  productQuantityDisplay.textContent = product.quantity
  updateCost();
}

function updateCost() {
    let totalCost = 0;
    for(let [sku, product] of Object.entries(products)) {
      totalCost += product.quantity * product.price;
    }
    costElement.textContent = String(totalCost);
}

(function() {
  var stripe = Stripe('pk_test_54LxtB4vZjsleKrRO5zqpuV1');

  var checkoutButton = document.getElementById('checkout-button');
  checkoutButton.addEventListener('click', function () {
    stripe.redirectToCheckout({
      items: Object.keys(products).map(sku => { return {sku: sku, quantity: products[sku].quantity} }),
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