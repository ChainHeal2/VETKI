/** Graba en el navegador y muestra la transcripción local devuelta por Flask. */
document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('btnVoiceRecord');
    const fabBtn = document.getElementById('btnVoiceRecordFab');
    const statusText = document.getElementById('voiceStatusText');
    const timer = document.getElementById('recordingTimer');
    const transcriptionField = document.getElementById('voiceTranscription');
    const distributeButton = document.getElementById('btnDistributeTranscription');
    const distributionStatus = document.getElementById('distributionStatus');
    if (!recordBtn && !fabBtn) return;

    const petId = (recordBtn && recordBtn.dataset.petId) || (fabBtn && fabBtn.dataset.petId);
    const recordButtons = [recordBtn, fabBtn].filter(Boolean);
    let recorder = null;
    let audioStream = null;
    let chunks = [];
    let isRecording = false;
    let timerInterval = null;
    let secondsElapsed = 0;

    function notify(message, isError = false) {
        const container = document.querySelector('.toast-container');
        if (!container || !window.bootstrap?.Toast) {
            alert(message);
            return;
        }
        const toast = document.createElement('div');
        toast.className = `toast align-items-center ${isError ? 'text-bg-danger' : 'text-bg-success'} border-0 shadow-lg mb-2`;
        toast.setAttribute('role', 'alert');
        const row = document.createElement('div');
        row.className = 'd-flex';
        const body = document.createElement('div');
        body.className = 'toast-body';
        body.textContent = message;
        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'btn-close btn-close-white me-2 m-auto';
        close.dataset.bsDismiss = 'toast';
        close.setAttribute('aria-label', 'Cerrar');
        row.append(body, close);
        toast.appendChild(row);
        container.appendChild(toast);
        new bootstrap.Toast(toast, { delay: 5000 }).show();
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }

    function numberFromSpanishWords(value) {
        const words = value.toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[.,;:!?]/g, ' ')
            .trim().split(/\s+/);
        const numberWords = {
            cero: 0, un: 1, uno: 1, una: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5,
            seis: 6, siete: 7, ocho: 8, nueve: 9, diez: 10, once: 11, doce: 12,
            trece: 13, catorce: 14, quince: 15, dieciseis: 16, diecisiete: 17,
            dieciocho: 18, diecinueve: 19, veinte: 20, veintiuno: 21, veintiun: 21,
            veintidos: 22, veintitres: 23, veinticuatro: 24, veinticinco: 25,
            veintiseis: 26, veintisiete: 27, veintiocho: 28, veintinueve: 29,
            treinta: 30, cuarenta: 40, cincuenta: 50, sesenta: 60, setenta: 70,
            ochenta: 80, noventa: 90, cien: 100, ciento: 100, doscientos: 200,
            trescientos: 300, cuatrocientos: 400, quinientos: 500, seiscientos: 600,
            setecientos: 700, ochocientos: 800, novecientos: 900
        };
        let start = 0;
        while (['es', 'son', 'de', 'en', 'a', 'aproximadamente', 'aprox', 'esta'].includes(words[start])) start++;
        let negative = false;
        if (words[start] === 'menos') {
            negative = true;
            start++;
        }

        let current = 0;
        let total = 0;
        let consumed = 0;
        for (let i = start; i < words.length; i++) {
            const word = words[i];
            if (word === 'y') continue;
            if (word === 'mil') {
                total += (current || 1) * 1000;
                current = 0;
            } else if (Object.hasOwn(numberWords, word)) {
                current += numberWords[word];
            } else {
                break;
            }
            consumed = i - start + 1;
        }
        if (!consumed) return null;
        const integer = total + current;
        const nextIndex = start + consumed;
        if (['coma', 'punto'].includes(words[nextIndex])) {
            const decimalDigits = [];
            for (let i = nextIndex + 1; i < words.length; i++) {
                const word = words[i];
                if (word === 'y') continue;
                if (!Object.hasOwn(numberWords, word)) break;
                decimalDigits.push(String(numberWords[word]));
            }
            if (decimalDigits.length) return `${negative ? '-' : ''}${integer}.${decimalDigits.join('')}`;
        }
        return `${negative ? '-' : ''}${integer}`;
    }

    function extractNumericValue(value) {
        const digits = value.match(/-?\d+(?:[.,]\d+)?/);
        if (digits) return digits[0].replace(',', '.');
        return numberFromSpanishWords(value);
    }

    function distributeTranscription() {
        const text = transcriptionField?.value.trim();
        if (!text) {
            if (distributionStatus) distributionStatus.textContent = 'Primero dicta o escribe la transcripción.';
            return;
        }

        const fieldsByKeyword = [
            { pattern: 'frecuencia\\s+card[ií]aca|ritmo\\s+card[ií]aco|pulso', id: 'medical_record_heart', numeric: true, name: 'frecuencia cardíaca' },
            { pattern: 'frecuencia\\s+respiratoria|respiraci[oó]n', id: 'medical_record_respiratory', numeric: true, name: 'frecuencia respiratoria' },
            { pattern: 'tiempo\\s+de\\s+llenado\\s+capilar|llenado\\s+capilar|capilar', id: 'medical_record_capillary', numeric: true, name: 'llenado capilar' },
            { pattern: 'presi[oó]n\\s+arterial|presi[oó]n', id: 'medical_record_arterial', numeric: true, name: 'presión arterial' },
            { pattern: 'temperatura', id: 'medical_record_temperature', numeric: true, name: 'temperatura' },
            { pattern: 'hidrataci[oó]n|agua', id: 'medical_record_water', numeric: true, name: 'hidratación' },
            { pattern: 'peso', id: 'medical_record_weight', numeric: true, name: 'peso' },
            { pattern: 'anamnesis|historia\\s+cl[ií]nica', id: 'medical_record_history', name: 'anamnesis' },
            { pattern: 'signos\\s+cl[ií]nicos|signos', id: 'medical_record_signals', name: 'signos clínicos' },
            { pattern: 'diagn[oó]stico', id: 'medical_record_diagnosis', name: 'diagnóstico' },
            { pattern: 'tratamiento|indicaciones', id: 'medical_record_treatment', name: 'tratamiento' },
            { pattern: 'motivo', id: 'medical_record_reason', reason: true, name: 'motivo' }
        ];
        const keywordPattern = new RegExp(`\\b(${fieldsByKeyword.map((field) => field.pattern).join('|')})\\b\\s*(?:(?:es|de)\\s*)?[:,-]?\\s*`, 'gi');
        const matches = [...text.matchAll(keywordPattern)];
        if (!matches.length) {
            if (distributionStatus) distributionStatus.textContent = 'No encontré palabras clave. Prueba: “peso ocho, temperatura treinta y ocho coma cinco, frecuencia cardíaca noventa”.';
            return;
        }

        let filled = 0;
        const skipped = [];
        matches.forEach((match, index) => {
            const keyword = match[1].toLowerCase();
            const field = fieldsByKeyword.find((candidate) => new RegExp(`^(?:${candidate.pattern})$`, 'i').test(keyword));
            if (!field) return;
            const start = match.index + match[0].length;
            const end = index + 1 < matches.length ? matches[index + 1].index : text.length;
            const value = text.slice(start, end).trim().replace(/^[,;:.\s-]+|[,;:.\s-]+$/g, '');
            const input = document.getElementById(field.id);
            if (!input || !value) return;
            if (input.value.trim()) {
                skipped.push(field.name);
                return;
            }

            if (field.numeric) {
                // El formulario guarda estos datos como un solo valor numérico; una presión como 120/80 requiere otro diseño de campo.
                if (/\d+(?:[.,]\d+)?\s*\/\s*\d/.test(value)) {
                    skipped.push(`${field.name} (formato no compatible)`);
                    return;
                }
                const numericValue = extractNumericValue(value);
                if (!numericValue) {
                    skipped.push(`${field.name} (no reconocí el número)`);
                    return;
                }
                input.value = numericValue;
            } else if (field.reason) {
                const reason = value.toLowerCase();
                const option = [...input.options].find((item) => item.value && reason.includes(item.textContent.trim().toLowerCase()));
                if (!option) {
                    skipped.push('motivo (indica preventiva, control o urgencia)');
                    return;
                }
                input.value = option.value;
            } else {
                input.value = value;
            }
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            filled++;
        });

        const summary = filled ? `Se completaron ${filled} campo${filled === 1 ? '' : 's'}.` : 'No se completaron campos.';
        const skippedMessage = skipped.length ? ` Revisa manualmente: ${[...new Set(skipped)].join(', ')}.` : '';
        if (distributionStatus) distributionStatus.textContent = `${summary}${skippedMessage} Verifica los valores antes de guardar.`;
    }

    function updateButtons(recording, processing = false) {
        isRecording = recording;
        recordButtons.forEach((button) => {
            button.disabled = processing;
            button.className = button.id === 'btnVoiceRecord'
                ? `btn btn-${recording ? 'danger' : processing ? 'secondary' : 'primary'} ${recording ? 'voice-recording-active ' : ''}rounded-pill px-4 py-2 d-inline-flex align-items-center gap-2 shadow-sm`
                : `btn btn-${recording ? 'danger' : processing ? 'secondary' : 'primary'} voice-record-fab ${recording ? 'voice-recording-active ' : ''}shadow-lg`;
            button.innerHTML = processing
                ? '<span class="spinner-border spinner-border-sm" role="status"></span>'
                : recording
                    ? '<i class="bi bi-stop-circle-fill fs-5"></i> <span>Detener dictado</span>'
                    : '<i class="bi bi-mic-fill fs-5"></i> <span>Dictar por Voz</span>';
            if (button.id === 'btnVoiceRecordFab' && !processing) {
                button.innerHTML = recording
                    ? '<i class="bi bi-stop-circle-fill fs-4"></i>'
                    : '<i class="bi bi-mic-fill fs-4"></i>';
            }
        });

        if (statusText) {
            statusText.textContent = processing
                ? 'Transcribiendo audio en el servidor local...'
                : recording
                    ? 'Grabando... habla con claridad y detén el dictado al terminar.'
                    : 'Presiona el micrófono para iniciar el dictado.';
            statusText.className = processing
                ? 'small text-info fw-bold mb-0'
                : recording
                    ? 'small text-danger fw-bold mb-0'
                    : 'small text-muted mb-0';
        }
    }

    function updateTimer() {
        secondsElapsed++;
        const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
        const secs = String(secondsElapsed % 60).padStart(2, '0');
        if (timer) timer.textContent = `${mins}:${secs}`;
    }

    function getCsrfToken() {
        const input = document.querySelector('input[name="csrf_token"], input[name$="-csrf_token"]');
        return input?.value || document.querySelector('meta[name="csrf-token"]')?.content || '';
    }

    async function sendAudio(blob, mimeType) {
        updateButtons(false, true);
        const extension = mimeType.includes('mp4') ? 'mp4'
            : mimeType.includes('ogg') ? 'ogg'
                : mimeType.includes('wav') ? 'wav' : 'webm';
        const formData = new FormData();
        formData.append('audio', blob, `dictado.${extension}`);
        formData.append('pet_id', petId || '');

        try {
            const token = getCsrfToken();
            const response = await fetch('/api/clinical-voice-intake', {
                method: 'POST',
                headers: token ? { 'X-CSRFToken': token } : {},
                body: formData
            });
            const responseText = await response.text();
            let data = {};
            try {
                data = responseText ? JSON.parse(responseText) : {};
            } catch {
                throw new Error(`El servidor respondió HTTP ${response.status}, pero no devolvió JSON.`);
            }
            if (!response.ok) {
                throw new Error(data.error || data.message || `El servidor respondió HTTP ${response.status}.`);
            }
            if (typeof data.transcription !== 'string') {
                throw new Error('El servidor no devolvió el texto transcrito.');
            }
            if (transcriptionField) {
                const previous = transcriptionField.value.trim();
                transcriptionField.value = previous
                    ? `${previous}\n${data.transcription}`
                    : data.transcription;
            }
            notify('Transcripción lista. Revísala y edítala si hace falta.');
        } catch (error) {
            console.error('Error al transcribir el audio:', error);
            notify(error.message || 'No se pudo transcribir el audio.', true);
        } finally {
            updateButtons(false);
        }
    }

    async function startRecording() {
        if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
            notify('Este navegador no permite grabar audio desde esta página.', true);
            return;
        }
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            chunks = [];
            const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg', 'audio/mp4'];
            const mimeType = mimeTypes.find((type) => MediaRecorder.isTypeSupported(type));
            recorder = mimeType
                ? new MediaRecorder(audioStream, { mimeType })
                : new MediaRecorder(audioStream);

            recorder.ondataavailable = (event) => {
                if (event.data?.size) chunks.push(event.data);
            };
            recorder.onerror = (event) => {
                console.error('Error de MediaRecorder:', event.error);
                notify('Ocurrió un error al grabar el audio.', true);
            };
            recorder.onstop = () => {
                const actualMimeType = recorder.mimeType || 'audio/webm';
                const blob = new Blob(chunks, { type: actualMimeType });
                audioStream?.getTracks().forEach((track) => track.stop());
                audioStream = null;
                if (!blob.size) {
                    notify('No se detectó audio. Intenta nuevamente.', true);
                    updateButtons(false);
                    return;
                }
                sendAudio(blob, actualMimeType);
            };

            recorder.start(250);
            secondsElapsed = 0;
            if (timer) timer.textContent = '00:00';
            timerInterval = setInterval(updateTimer, 1000);
            updateButtons(true);
        } catch (error) {
            console.error('No se pudo iniciar la grabación:', error);
            audioStream?.getTracks().forEach((track) => track.stop());
            audioStream = null;
            notify(error.name === 'NotAllowedError'
                ? 'Permite el acceso al micrófono en tu navegador e inténtalo de nuevo.'
                : 'No se pudo acceder al micrófono.', true);
            updateButtons(false);
        }
    }

    function stopRecording() {
        if (recorder?.state === 'recording') recorder.stop();
        clearInterval(timerInterval);
        timerInterval = null;
        updateButtons(false, true);
    }

    recordButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            if (isRecording) stopRecording();
            else startRecording();
        });
    });

    distributeButton?.addEventListener('click', distributeTranscription);

    window.addEventListener('pagehide', () => {
        if (recorder?.state === 'recording') recorder.stop();
        audioStream?.getTracks().forEach((track) => track.stop());
        clearInterval(timerInterval);
    });
});
