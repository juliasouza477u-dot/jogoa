// Aplicativo otimizado para celular: prevent zoom em duplo toque em botões
document.addEventListener('DOMContentLoaded', function () {
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function (event) {
        const now = Date.now();
        const delta = now - lastTouchEnd;
        if (delta > 0 && delta < 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, { passive: false });

    // Evita zoom duplo-toque em inputs e botões
    const clickables = document.querySelectorAll('button, input, a');
    clickables.forEach(function (el) {
        el.addEventListener('touchend', function (e) {
            e.preventDefault();
        }, { passive: false });
    });
});