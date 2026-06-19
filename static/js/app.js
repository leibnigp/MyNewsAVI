// HTMX config and minor interactivity
htmx.config.globalViewTransitions = false;

// Auto-submit filter form on select/input change
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;

    filterForm.querySelectorAll('select, input[type="text"]').forEach(el => {
        el.addEventListener('change', function() {
            htmx.trigger(filterForm, 'submit');
        });
    });
});
