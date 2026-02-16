// ============================================
// Aura Landing Page — Futuristic Interactions
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Terminal typing effect
    const terminalLines = document.querySelectorAll('.terminal-line');
    terminalLines.forEach((line, i) => {
        line.style.opacity = '0';
        line.style.transform = 'translateX(-6px)';
        line.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => {
            line.style.opacity = '1';
            line.style.transform = 'translateX(0)';
        }, 400 + i * 180);
    });
});
