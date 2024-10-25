var stripe = Stripe('pk_test_51QComsAhxaIXSN29f0PnP8AkkKWQ7CqYss3SNnmbjq02XmpA3FtyIR86XszJkkhxrndmGCHaCyBeBlX0DVYu0OpD008HnI93Ht');
var elements = stripe.elements();

var card = elements.create('card');
card.mount('#card-element');

document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    stripe.createToken(card).then(function(result) {
        if (result.error) {
            // Show error in payment form
            console.error(result.error.message);
        } else {
            // Add token to form
            var form = document.querySelector('form');
            var hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'stripeToken');
            hiddenInput.setAttribute('value', result.token.id);
            form.appendChild(hiddenInput);
            form.submit();
        }
    });
});
