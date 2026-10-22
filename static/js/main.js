// Smart Campus Placement Analyser Client Controller
console.log('Smart Campus Placement Analyser UI Engine Initialized.');

// Auto dismiss flash alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.animate-fade-in');
    alerts.forEach(el => {
        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transition = 'opacity 0.5s ease';
            setTimeout(() => el.remove(), 500);
        }, 6000);
    });
});
