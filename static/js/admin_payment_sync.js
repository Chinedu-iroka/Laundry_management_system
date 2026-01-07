document.addEventListener('DOMContentLoaded', function () {
    const paymentStatus = document.getElementById('id_payment_status');
    const totalPrice = document.getElementById('id_total_price');
    const amountPaid = document.getElementById('id_amount_paid');
    const balance = document.getElementById('id_balance');

    if (paymentStatus && totalPrice && amountPaid && balance) {
        paymentStatus.addEventListener('change', function () {
            if (this.value === 'paid') {
                amountPaid.value = totalPrice.value;
                balance.value = '0.00';
            } else if (this.value === 'pending') {
                amountPaid.value = '0.00';
                balance.value = totalPrice.value;
            }
        });

        // Also sync if total_price or amount_paid changes manually
        const updateBalance = () => {
            const total = parseFloat(totalPrice.value) || 0;
            const paid = parseFloat(amountPaid.value) || 0;
            balance.value = (total - paid).toFixed(2);

            // Auto-update status based on numbers? 
            // Better to let user explicitly set status but we update numbers based on status as requested.
        };

        totalPrice.addEventListener('input', updateBalance);
        amountPaid.addEventListener('input', updateBalance);
    }
});
