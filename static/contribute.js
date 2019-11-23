const checkoutButton = document.getElementById("checkout-button");
const shippingSelect = document.getElementById('shipping-select');

function addProduct(sku, amount) {
  const product = products[sku];
  product.quantity += amount;
  if (product.quantity < 0) product.quantity = 0;
  updateQuantityDisplay(sku);
  updateCost();
}

function addDonation(sku, amount) {
  const donation = donations[sku];
  donation.quantity += amount;
  if (donation.quantity < 0) donation.quantity = 0;
  updateCost();
}

function updateQuantityDisplay(sku) {
  const productQuantityDisplay = document.getElementById(sku);
  productQuantityDisplay.textContent = products[sku].quantity;
}

function updateCost() {
    let totalCost = 0;
    for(let product of Object.values(products).concat(Object.values(donations), Object.values(shipping))) {
      totalCost += product.quantity * product.price;
    }
    checkoutButton.textContent = "Checkout " + totalCost.toLocaleString('en-AU', {currency: 'AUD', currencyDisplay: 'symbol', style: 'currency'});
}

(function updateShipping() {
  shippingSelect.addEventListener('change', (event) => {
    const internationalShipping = parseInt(event.target.value);
    Object.values(shipping)[0].quantity = internationalShipping;
    updateCost();
    const shippingMessageElement = document.getElementById('shipping-message');
    if(internationalShipping) {
      shippingMessageElement.textContent = "+$5.00 international shipping";
    } else {
      shippingMessageElement.textContent = "";
    }
  });
})();

(function() {
  const stripe_test = 'pk_test_54LxtB4vZjsleKrRO5zqpuV1';

  var stripe = Stripe(stripe_test);

  var checkoutButton = document.getElementById('checkout-button');
  checkoutButton.addEventListener('click', function () {
    const productLineItems = Object.values(products).filter(sku => sku.quantity > 0).map(sku => { return {sku: sku.id, quantity: sku.quantity} })
    const donationLineItems = Object.values(donations).filter(sku => sku.quantity > 0).map(sku => { return {sku: sku.id, quantity: sku.quantity} })
    const shippingLineItems = Object.values(shipping).filter(sku => sku.quantity > 0).map(sku => { return {sku: sku.id, quantity: sku.quantity} })
    const lineItems = productLineItems.concat(donationLineItems, shippingLineItems);
    console.log(lineItems);
    if(shippingSelect.value == '') {
      alert('Select shipping region');
      return;
    }
    if(productLineItems.length == 0) {
      alert('Select postcards');
      return;
    }
    stripe.redirectToCheckout({
      items: lineItems,
      successUrl: 'https://www.psyclonicstudios.com.au/payment_success',
      cancelUrl: 'https://www.psyclonicstudios.com.au/contribute',
    })
    .then(function (result) {
      if (result.error) {
        var displayError = document.getElementById('error-message');
        displayError.textContent = result.error.message;
      }
    });
  });
})();