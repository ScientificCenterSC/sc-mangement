// Replace tabs logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        document.querySelectorAll('.view-section').forEach(c => c.classList.remove('active'));
        document.getElementById(this.dataset.target).classList.add('active');
    });
});
