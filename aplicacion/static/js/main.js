/**
 * VETKI - Núcleo JavaScript Global
 * Inicializa componentes interactivos de Bootstrap y manejadores comunes.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicialización automática de Toasts de Bootstrap 5
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(toastEl => {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    });

    // 2. Manejo de botones de envío con estado de carga (Loading State)
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            // No interceptar si el formulario no es válido
            if (!this.checkValidity()) return;

            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const loadingText = submitBtn.dataset.loadingText || 'Procesando...';
                
                // Guardar contenido original por si se necesita
                submitBtn.dataset.originalContent = submitBtn.innerHTML || submitBtn.value;
                submitBtn.disabled = true;

                if (submitBtn.tagName === 'BUTTON') {
                    submitBtn.innerHTML = `
                        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        <span>${loadingText}</span>
                    `;
                } else {
                    submitBtn.value = loadingText;
                }

                // Si no se canceló el submit, proceder
                setTimeout(() => {
                    // Timeout de seguridad en caso de fallo de red
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        if (submitBtn.tagName === 'BUTTON') {
                            submitBtn.innerHTML = submitBtn.dataset.originalContent;
                        } else {
                            submitBtn.value = submitBtn.dataset.originalContent;
                        }
                    }
                }, 10000);
            }
        });
    });
});

