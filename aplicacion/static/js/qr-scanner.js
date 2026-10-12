/**
 * VETKI - Módulo Reutilizable de Lector QR / Microchip
 * Utiliza Html5Qrcode para escanear etiquetas y microchips de pacientes.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Escáner de Búsqueda Global en Dashboard (dashboardQrModal)
    initModalScanner({
        modalId: 'dashboardQrModal',
        readerId: 'dashboardQrReader',
        statusId: 'dashboardQrStatus',
        onSuccess: async (decodedText, modalEl, statusEl, scanner) => {
            try {
                await scanner.stop();
                statusEl.innerHTML = '<span class="spinner-border spinner-border-sm text-primary me-2" role="status"></span> Procesando...';
                
                const processUrl = modalEl.dataset.processUrl || '/api/qr/process';
                const resultsUrl = modalEl.dataset.resultsUrl || '/pet_search';
                const token = modalEl.querySelector('input[name="csrf_token"]')?.value || '';

                const response = await fetch(processUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': token
                    },
                    body: JSON.stringify({ content: decodedText })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Código inválido.');

                window.location.href = `${resultsUrl}?microchip=${encodeURIComponent(result.microchip)}`;
            } catch (error) {
                statusEl.innerHTML = `<i class="bi bi-x-circle text-danger me-1"></i> ${error.message || 'Error en la lectura.'}`;
            }
        }
    });

    // 2. Escáner de Carga de Microchip en Formulario de Paciente (qrScannerModal)
    initModalScanner({
        modalId: 'qrScannerModal',
        readerId: 'qr-reader',
        statusId: 'qr-status',
        onSuccess: async (decodedText, modalEl, statusEl, scanner) => {
            try {
                await scanner.stop();
                statusEl.textContent = 'Procesando código...';
                
                const processUrl = modalEl.dataset.processUrl || '/api/qr/process';
                const token = document.querySelector('input[name="csrf_token"]')?.value || '';
                const inputMicrochip = document.getElementById('pet_microchip');

                const response = await fetch(processUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': token
                    },
                    body: JSON.stringify({ content: decodedText })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'QR inválido');

                if (inputMicrochip) {
                    inputMicrochip.value = result.microchip;
                }
                statusEl.textContent = 'Microchip cargado correctamente.';
                
                const bsModal = bootstrap.Modal.getInstance(modalEl);
                if (bsModal) bsModal.hide();
            } catch (error) {
                statusEl.textContent = error.message || 'Error al procesar microchip.';
            }
        }
    });
});

/**
 * Helper para inicializar modales de escaneo Html5Qrcode
 */
function initModalScanner({ modalId, readerId, statusId, onSuccess }) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const status = document.getElementById(statusId);
    let scanner = null;

    modal.addEventListener('shown.bs.modal', async () => {
        if (!window.isSecureContext) {
            if (status) status.innerHTML = '<i class="bi bi-shield-exclamation text-warning me-1"></i> La cámara requiere HTTPS.';
            return;
        }
        if (!window.Html5Qrcode) {
            if (status) status.textContent = 'No se pudo cargar el lector QR.';
            return;
        }

        scanner = new Html5Qrcode(readerId);
        try {
            await scanner.start(
                { facingMode: 'environment' },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                async (decodedText) => {
                    if (onSuccess) await onSuccess(decodedText, modal, status, scanner);
                }
            );
        } catch (err) {
            if (status) status.textContent = 'Permiso denegado. Habilita la cámara en tu navegador.';
        }
    });

    modal.addEventListener('hidden.bs.modal', async () => {
        if (scanner) {
            try { await scanner.stop(); } catch (_) {}
            scanner.clear();
            scanner = null;
        }
        if (status) status.textContent = 'Apunta la cámara al código del paciente.';
    });
}

