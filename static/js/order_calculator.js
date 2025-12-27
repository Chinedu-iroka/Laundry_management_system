// static/js/order_calculator.js
document.addEventListener('DOMContentLoaded', function() {
    let selectedItems = {};
    const expressCharge = 5.00; // Configurable
    
    // Item selection logic
    document.querySelectorAll('.item-card').forEach(card => {
        const itemId = card.dataset.id;
        const price = parseFloat(card.dataset.price);
        
        card.querySelector('.btn-plus').addEventListener('click', function() {
            const input = card.querySelector('.item-quantity');
            let quantity = parseInt(input.value) + 1;
            input.value = quantity;
            updateItem(itemId, quantity, price);
        });
        
        // Similar for minus button
    });
    
    function updateItem(itemId, quantity, price) {
        if (quantity > 0) {
            selectedItems[itemId] = {quantity, price};
        } else {
            delete selectedItems[itemId];
        }
        calculateTotal();
        updateSelectedList();
    }
    
    function calculateTotal() {
        let subtotal = 0;
        Object.values(selectedItems).forEach(item => {
            subtotal += item.quantity * item.price;
        });
        
        const expressChecked = document.getElementById('express-service').checked;
        const express = expressChecked ? expressCharge : 0;
        const total = subtotal + express;
        
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('express-charge').textContent = `$${express.toFixed(2)}`;
        document.getElementById('total-amount').textContent = `$${total.toFixed(2)}`;
        
        // Update hidden form fields
        document.getElementById('id_subtotal').value = subtotal;
        document.getElementById('id_total_amount').value = total;
    }
});