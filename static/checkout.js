'use strict';

var stripe = Stripe('pk_test_54LxtB4vZjsleKrRO5zqpuV1');

function registerElements(elements) {
  var formSelector = '#checkout';
  var form = document.querySelector(formSelector);

  var error = form.querySelector('.error');
  var errorMessage = error.querySelector('.message');

  function enableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function (input) {
        input.removeAttribute('disabled');
      }
    );
  }

  function disableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function (input) {
        input.setAttribute('disabled', 'true');
      }
    );
  }

  function triggerBrowserValidation() {
    // The only way to trigger HTML5 form validation UI is to fake a user submit
    // event.
    var submit = document.createElement('input');
    submit.type = 'submit';
    submit.style.display = 'none';
    form.appendChild(submit);
    submit.click();
    submit.remove();
  }

  // Listen for errors from each Element, and show error messages in the UI.
  var savedErrors = {};
  elements.forEach(function (element, idx) {
    element.on('change', function (event) {
      if (event.error) {
        error.classList.add('visible');
        savedErrors[idx] = event.error.message;
        errorMessage.innerText = event.error.message;
      } else {
        savedErrors[idx] = null;

        // Loop over the saved errors and find the first one, if any.
        var nextError = Object.keys(savedErrors)
          .sort()
          .reduce(function (maybeFoundError, key) {
            return maybeFoundError || savedErrors[key];
          }, null);

        if (nextError) {
          // Now that they've fixed the current error, show another one.
          errorMessage.innerText = nextError;
        } else {
          // The user fixed the last error; no more errors.
          error.classList.remove('visible');
        }
      }
    });
  });

  // Listen on the form's 'submit' handler...
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Trigger HTML5 validation UI on the form if any of the inputs fail
    // validation.
    var plainInputsValid = true;
    Array.prototype.forEach.call(form.querySelectorAll('input'), function (
      input
    ) {
      if (input.checkValidity && !input.checkValidity()) {
        plainInputsValid = false;
        return;
      }
    });
    if (!plainInputsValid) {
      triggerBrowserValidation();
      return;
    }

    // Show a loading screen...
    checkout.classList.add('submitting');

    // Disable all inputs.
    disableInputs();

    // Gather additional customer data we may have collected in our form.
    var name = form.querySelector('#name');
    var email = form.querySelector('#email');
    var street = form.querySelector('#address');
    var city = form.querySelector('#city');
    var state = form.querySelector('#state');
    var postcode = form.querySelector('#postcode');
    var country = form.querySelector('#country');
    var additionalData = {
      name: name ? name.value : undefined,
      email: email ? email.value : undefined,
      address_line1: street ? street.value : undefined,
      address_city: city ? city.value : undefined,
      address_state: state ? state.value : undefined,
      address_zip: postcode ? postcode.value : undefined,
      address_country: country ? country.value : undefined
    };

    stripe.confirmCardPayment(form.dataset.secret, {
      payment_method: {
        card: elements[0],
      },
      receipt_email: additionalData.email,
      shipping: {
        address: {
          line1: additionalData.address_line1,
          city: additionalData.address_city,
          state: additionalData.address_state,
          country: additionalData.address_country,
          postal_code: additionalData.address_zip
        },
        name: additionalData.name
      },
      return_url: new URL("payment_success", window.location.origin).href
    }).then(function (result) {
      checkout.classList.remove('submitting');
      if (result.error) {
        // Show error to your customer (e.g., insufficient funds)
        enableInputs();
        errorMessage.innerText = result.error.message
      }
    });
  })
}

(function () {
  'use strict';

  var elements = stripe.elements({
    // Stripe's checkouts are localized to specific languages, but if
    // you wish to have Elements automatically detect your user's locale,
    // use `locale: 'auto'` instead.
    locale: window.__checkoutLocale,
  });

  var elementStyles = {
    base: {
      fontSize: "20px"
    },
    invalid: {
      color: '#fff',
      ':focus': {
        color: '#FA755A',
      },
      '::placeholder': {
        color: '#FFCCA5',
      },
    },
  };

  var elementClasses = {
    focus: 'focus',
    empty: 'empty',
    invalid: 'invalid',
  };

  var cardNumber = elements.create('cardNumber', {
    style: elementStyles,
    classes: elementClasses,
  });
  cardNumber.mount('#card-number');

  var cardExpiry = elements.create('cardExpiry', {
    style: elementStyles,
    classes: elementClasses,
  });
  cardExpiry.mount('#card-expiry');

  var cardCvc = elements.create('cardCvc', {
    style: elementStyles,
    classes: elementClasses,
  });
  cardCvc.mount('#card-cvc');

  registerElements([cardNumber, cardExpiry, cardCvc]);
})();