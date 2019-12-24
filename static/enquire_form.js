const addToCartButton = document.getElementById('add-to-cart-button');
const buyButton = document.getElementById('buy-button');
const buyForm = document.getElementById('buy-form');
const buyResetButton = document.getElementById('buy-reset');
const enquireButton = document.getElementById('enquire-button');
const enquireForm = document.getElementById('enquire-form');
const enquireResetButton = document.getElementById('enquire-reset');

(() => {
    if (buyButton) {
        buyButton.addEventListener('click', () => {
            enquireForm.hidden = true;
            buyForm.hidden = !buyForm.hidden;
        })
        buyResetButton.addEventListener('click', () => {
            enquireForm.hidden = true;
            buyForm.hidden = true;
        })
    }
    enquireButton.addEventListener('click', () => {
        enquireForm.hidden = !enquireForm.hidden;
        if (buyButton) {
            buyForm.hidden = true;
        }
    })
    enquireResetButton.addEventListener('click', () => {
        enquireForm.hidden = true;
        if (buyButton) {
            buyForm.hidden = true;
        }
    })
})();