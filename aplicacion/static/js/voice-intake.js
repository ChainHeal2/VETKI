/**
 * VETKI - Asistente de Dictado Clínico por Voz e Inteligencia Artificial
 *
 * Captura audio con MediaRecorder API, envía al endpoint /api/clinical-voice-intake
 * y mapea la respuesta estructurada a los campos del formulario con feedback visual.
 */

document.addEventListener('DOMContentLoaded', () => {
    const voiceCard = document.getElementById('voiceIntakeCard');
    const recordBtn = document.getElementById('btnVoiceRecord');
    const fabBtn = document.getElementById('btnVoiceRecordFab');
    const voiceStatusText = document.getElementById('voiceStatusText');
    const recordingTimer = document.getElementById('recordingTimer');

    if (!recordBtn && !fabBtn) {
        return;
    }

    // Identificador de la mascota para el endpoint
    const petId = (recordBtn && recordBtn.dataset.petId) || (fabBtn && fabBtn.dataset.petId);

    // Variables de estado del grabador
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let timerInterval = null;
    let secondsElapsed = 0;
    let audioStream = null;

    // Elementos del DOM del formulario
    const formFields = {
        weight: document.getElementById('medical_record_weight'),
        temperature: document.getElementById('medical_record_temperature'),
        diagnosis: document.getElementById('medical_record_diagnosis'),
        history: document.getElementById('medical_record_history'),
        signals: document.getElementById('medical_record_signals'),
        treatment: document.getElementById('medical_record_treatment')
    };

    /**
     * Muestra notificación Toast flotante
     */
    function showNotification(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            alert(message);
            return;
        }

        const bgClass = type === 'success' ? 'text-bg-success' : (type === 'danger' ? 'text-bg-danger' : 'text-bg-primary');
        const iconClass = type === 'success' ? 'bi-check-circle' : (type === 'danger' ? 'bi-exclamation-triangle' : 'bi-info-circle');

        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center ${bgClass} border-0 shadow-lg mb-2`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2 fw-medium">
                    <i class="bi ${iconClass} fs-5"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
            </div>
        `;

        toastContainer.appendChild(toastEl);
        const toastInstance = new bootstrap.Toast(toastEl, { delay: 5000 });
        toastInstance.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    /**
     * Obtiene el token CSRF disponible en el formulario o meta tags
     */
    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        const metaCsrf = document.querySelector('meta[name="csrf-token"]');
        if (metaCsrf && metaCsrf.content) {
            return metaCsrf.content;
        }
        return '';
    }

    /**
     * Actualiza la interfaz según el estado de la grabación
     */
    function updateUIState(state) {
        if (state === 'idle') {
            isRecording = false;
            clearInterval(timerInterval);
            secondsElapsed = 0;
            if (recordingTimer) recordingTimer.textContent = '00:00';

            // Botón principal
            if (recordBtn) {
                recordBtn.disabled = false;
                recordBtn.className = 'btn btn-primary rounded-pill px-4 py-2 d-inline-flex align-items-center gap-2 shadow-sm';
                recordBtn.innerHTML = '<i class="bi bi-mic-fill fs-5"></i> <span>Dictar por Voz</span>';
            }

            // Botón FAB
            if (fabBtn) {
                fabBtn.disabled = false;
                fabBtn.className = 'btn btn-primary voice-record-fab shadow-lg';
                fabBtn.innerHTML = '<i class="bi bi-mic-fill fs-4"></i>';
            }

            if (voiceStatusText) {
                voiceStatusText.textContent = 'Presiona el micrófono para iniciar el dictado clínico.';
                voiceStatusText.className = 'small text-muted mb-0';
            }
        } else if (state === 'recording') {
            isRecording = true;
            secondsElapsed = 0;
            if (recordingTimer) recordingTimer.textContent = '00:00';
            timerInterval = setInterval(() => {
                secondsElapsed++;
                const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
                const secs = String(secondsElapsed % 60).padStart(2, '0');
                if (recordingTimer) recordingTimer.textContent = `${mins}:${secs}`;
            }, 1000);

            // Botón principal
            if (recordBtn) {
                recordBtn.disabled = false;
                recordBtn.className = 'btn btn-danger voice-recording-active rounded-pill px-4 py-2 d-inline-flex align-items-center gap-2 shadow-sm';
                recordBtn.innerHTML = '<i class="bi bi-stop-circle-fill fs-5"></i> <span>Detener y Procesar</span>';
            }

            // Botón FAB
            if (fabBtn) {
                fabBtn.disabled = false;
                fabBtn.className = 'btn btn-danger voice-record-fab voice-recording-active shadow-lg';
                fabBtn.innerHTML = '<i class="bi bi-stop-circle-fill fs-4"></i>';
            }

            if (voiceStatusText) {
                voiceStatusText.textContent = 'Escuchando... Menciona peso, constantes, diagnóstico y recetas.';
                voiceStatusText.className = 'small text-danger fw-bold mb-0';
            }
        } else if (state === 'processing') {
            isRecording = false;
            clearInterval(timerInterval);

            // Botón principal
            if (recordBtn) {
                recordBtn.disabled = true;
                recordBtn.className = 'btn btn-secondary rounded-pill px-4 py-2 d-inline-flex align-items-center gap-2 shadow-sm';
                recordBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> <span>Procesando con IA...</span>';
            }

            // Botón FAB
            if (fabBtn) {
                fabBtn.disabled = true;
                fabBtn.className = 'btn btn-secondary voice-record-fab shadow-lg';
                fabBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
            }

            if (voiceStatusText) {
                voiceStatusText.textContent = 'La IA está estructurando la información clínica...';
                voiceStatusText.className = 'small text-info fw-bold mb-0';
            }
        }
    }

    /**
     * Aplica el efecto de resaltado visual al campo rellenado por la IA
     */
    function highlightField(inputElement) {
        if (!inputElement) return;

        inputElement.classList.remove('ai-field-updated');
        void inputElement.offsetWidth; // Trigger reflow
        inputElement.classList.add('ai-field-updated');

        // Si el campo está en una pestaña no activa, alertar con un badge en el tab
        const parentTabPane = inputElement.closest('.tab-pane');
        if (parentTabPane && !parentTabPane.classList.contains('active')) {
            const tabId = parentTabPane.getAttribute('id');
            const tabBtn = document.querySelector(`[data-bs-target="#${tabId}"]`);
            if (tabBtn && !tabBtn.querySelector('.tab-ai-badge')) {
                const badge = document.createElement('span');
                badge.className = 'tab-ai-badge';
                badge.title = 'Datos actualizados por IA';
                tabBtn.appendChild(badge);
            }
        }
    }

    /**
     * Rellena los inputs del formulario clínico con la respuesta estructurada de la IA
     */
    function populateFormFields(data) {
        let fieldsUpdatedCount = 0;

        // 1. Constantes vitales (patient_updates)
        const patientUpdates = data.patient_updates || {};
        if (patientUpdates.weight_kg !== null && patientUpdates.weight_kg !== undefined) {
            if (formFields.weight) {
                formFields.weight.value = patientUpdates.weight_kg;
                highlightField(formFields.weight);
                fieldsUpdatedCount++;
            }
        }

        if (patientUpdates.temperature_c !== null && patientUpdates.temperature_c !== undefined) {
            if (formFields.temperature) {
                formFields.temperature.value = patientUpdates.temperature_c;
                highlightField(formFields.temperature);
                fieldsUpdatedCount++;
            }
        }

        // 2. Registro clínico (clinical_record)
        const clinicalRecord = data.clinical_record || {};
        if (clinicalRecord.diagnosis) {
            if (formFields.diagnosis) {
                formFields.diagnosis.value = clinicalRecord.diagnosis;
                highlightField(formFields.diagnosis);
                fieldsUpdatedCount++;
            }
        }

        if (clinicalRecord.observations) {
            // Si el campo de historia está vacío, o agregamos observaciones al historial
            if (formFields.history && !formFields.history.value.trim()) {
                formFields.history.value = clinicalRecord.observations;
                highlightField(formFields.history);
                fieldsUpdatedCount++;
            } else if (formFields.signals) {
                formFields.signals.value = clinicalRecord.observations;
                highlightField(formFields.signals);
                fieldsUpdatedCount++;
            }
        }

        // 3. Prescripciones / Fármacos recetados (prescriptions)
        const prescriptions = data.prescriptions || [];
        if (prescriptions.length > 0 && formFields.treatment) {
            const prescriptionLines = prescriptions.map((rx) => {
                const parts = [];
                if (rx.dosage) parts.push(`Dosis: ${rx.dosage}`);
                if (rx.frequency) parts.push(`Frecuencia: ${rx.frequency}`);
                if (rx.duration) parts.push(`Duración: ${rx.duration}`);
                return `• ${rx.drug_name}: ${parts.join(', ')}`;
            });

            const currentTreatment = formFields.treatment.value.trim();
            const formattedRxText = prescriptionLines.join('\n');

            if (currentTreatment) {
                formFields.treatment.value = `${currentTreatment}\n\nPrescripción (IA):\n${formattedRxText}`;
            } else {
                formFields.treatment.value = `Prescripción:\n${formattedRxText}`;
            }
            highlightField(formFields.treatment);
            fieldsUpdatedCount++;
        }

        return fieldsUpdatedCount;
    }

    /**
     * Envía el audio grabado al backend /api/clinical-voice-intake
     */
    async function sendAudioToBackend(audioBlob, mimeType) {
        updateUIState('processing');

        try {
            const formData = new FormData();
            
            // Determinar extensión según el tipo mime
            let filename = 'dictado.webm';
            if (mimeType.includes('mp4')) {
                filename = 'dictado.mp4';
            } else if (mimeType.includes('ogg')) {
                filename = 'dictado.ogg';
            } else if (mimeType.includes('wav')) {
                filename = 'dictado.wav';
            }

            formData.append('audio', audioBlob, filename);
            if (petId) {
                formData.append('pet_id', petId);
            }

            const csrfToken = getCsrfToken();
            const headers = {};
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
                headers['X-CSRF-Token'] = csrfToken;
            }

            const response = await fetch('/api/clinical-voice-intake', {
                method: 'POST',
                headers: headers,
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMsg = data.error || 'Error al procesar el dictado con IA.';
                showNotification(errorMsg, 'danger');
                updateUIState('idle');
                return;
            }

            // Éxito: autocompletar campos
            const updatedCount = populateFormFields(data);
            showNotification(`¡Dictado procesado! Se autocompletaron ${updatedCount} campos. Revisa y edita según sea necesario.`, 'success');

        } catch (error) {
            console.error('Error al enviar audio al servidor:', error);
            showNotification('Ocurrió un problema de conexión al enviar el audio.', 'danger');
        } finally {
            updateUIState('idle');
        }
    }

    /**
     * Inicia la captura de audio por micrófono
     */
    async function startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showNotification('Tu navegador móvil no tiene soporte para grabación de audio.', 'danger');
            return;
        }

        try {
            audioChunks = [];
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Identificar formato soportado por el navegador
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options = { mimeType: 'audio/webm;codecs=opus' };
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                options = { mimeType: 'audio/mp4' };
            } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
                options = { mimeType: 'audio/ogg' };
            }

            mediaRecorder = new MediaRecorder(audioStream, options);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const mimeType = mediaRecorder.mimeType || 'audio/webm';
                const audioBlob = new Blob(audioChunks, { type: mimeType });

                // Detener todas las pistas de audio para liberar el hardware del micrófono
                if (audioStream) {
                    audioStream.getTracks().forEach((track) => track.stop());
                }

                if (audioBlob.size === 0) {
                    showNotification('No se detectó audio grabado. Intenta nuevamente.', 'danger');
                    updateUIState('idle');
                    return;
                }

                sendAudioToBackend(audioBlob, mimeType);
            };

            mediaRecorder.start(250); // Recolectar fragmentos cada 250ms
            updateUIState('recording');

        } catch (err) {
            console.error('Error de acceso al micrófono:', err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showNotification('Permiso de micrófono denegado. Por favor, habilítalo en la configuración de tu navegador.', 'danger');
            } else {
                showNotification('No se pudo acceder al micrófono del dispositivo.', 'danger');
            }
            updateUIState('idle');
        }
    }

    /**
     * Detiene la captura de audio
     */
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    }

    /**
     * Alternar estado de grabación al interactuar con los botones
     */
    function toggleRecording() {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    }

    if (recordBtn) {
        recordBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleRecording();
        });
    }

    if (fabBtn) {
        fabBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleRecording();
        });
    }

    // Limpieza de badge de novedad al hacer clic en pestañas
    document.querySelectorAll('#medicalRecordTabs button[data-bs-toggle="pill"]').forEach((tabBtn) => {
        tabBtn.addEventListener('shown.bs.tab', () => {
            const badge = tabBtn.querySelector('.tab-ai-badge');
            if (badge) {
                badge.remove();
            }
        });
    });
});

