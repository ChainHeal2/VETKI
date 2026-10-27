/**
 * VETKI - Módulo de Agenda Clínica (FullCalendar v6)
 * Gestión responsive y adaptabilidad móvil.
 */

document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    const calendarContainer = document.getElementById('appointmentCalendar');
    const messageEl = document.getElementById('calendarMessage');
    const editModalEl = document.getElementById('appointmentEditModal');
    const editModalBody = document.getElementById('appointmentEditModalBody');
    const editPetLabel = document.getElementById('appointmentEditPet');
    const editModal = editModalEl && window.bootstrap
        ? bootstrap.Modal.getOrCreateInstance(editModalEl)
        : null;

    function showMessage(message, type) {
        if (!messageEl) return;
        messageEl.textContent = message;
        messageEl.className = `alert alert-${type} mb-3`;
    }

    function localDateTime(date) {
        const pad = value => String(value).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
            `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }

    async function openEditModal(event) {
        if (!editModal || !editModalBody || !event.url) {
            showMessage('No se pudo abrir el formulario de edición.', 'danger');
            return;
        }

        editModalBody.innerHTML = '<div class="text-center py-4" role="status">Cargando cita…</div>';
        editPetLabel.textContent = event.extendedProps.petName
            ? `Paciente: ${event.extendedProps.petName}`
            : '';
        editModal.show();

        try {
            const response = await fetch(event.url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const html = await response.text();
            if (!response.ok) {
                throw new Error('No se pudo cargar el formulario de la cita.');
            }

            editModalBody.innerHTML = html;
            const form = editModalBody.querySelector('#appointmentEditForm');
            form?.addEventListener('submit', async function (submitEvent) {
                submitEvent.preventDefault();
                const submitButton = form.querySelector('button[type="submit"]');
                const errorEl = form.querySelector('#appointmentEditError');
                submitButton.disabled = true;
                errorEl.classList.add('d-none');

                try {
                    const csrfToken = form.querySelector('input[name="csrf_token"]')?.value;
                    const saveResponse = await fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken || ''
                        },
                        body: new FormData(form)
                    });
                    const data = await saveResponse.json().catch(() => ({}));
                    if (!saveResponse.ok) {
                        throw new Error(data.error || 'No se pudo guardar la cita.');
                    }

                    editModal.hide();
                    calendar.refetchEvents();
                    showMessage(data.message || 'Cita actualizada.', 'success');
                } catch (error) {
                    errorEl.textContent = error.message || 'Error al guardar la cita.';
                    errorEl.classList.remove('d-none');
                } finally {
                    submitButton.disabled = false;
                }
            });
        } catch (error) {
            editModalBody.innerHTML = `<div class="alert alert-danger mb-0" role="alert">${error.message}</div>`;
        }
    }

    let isMobile = window.innerWidth < 768;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: isMobile ? 'listWeek' : 'dayGridMonth',
        locale: 'es',
        firstDay: 1,
        timeZone: 'local',
        height: 'auto',
        // Permite mover las citas dentro del calendario y guardar el horario.
        editable: true,
        eventStartEditable: true,
        eventDurationEditable: false,

        headerToolbar: isMobile ? {
            left: 'prev,next today',
            center: 'title',
            right: 'listWeek,dayGridMonth'
        } : {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },

        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Agenda'
        },

        events: '/appointments_list',

        eventDrop: async function (info) {
            const urlTemplate = calendarContainer?.dataset.moveUrlTemplate;
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!urlTemplate || !csrfToken || !info.event.start) {
                info.revert();
                showMessage('No se pudo preparar el cambio de horario.', 'danger');
                return;
            }

            const url = urlTemplate.replace(/\/\d+$/, `/${encodeURIComponent(info.event.id)}`);
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ start: localDateTime(info.event.start) })
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.error || 'No se pudo guardar el horario.');
                }
                showMessage(data.message || 'Horario actualizado.', 'success');
            } catch (error) {
                info.revert();
                showMessage(error.message || 'Error de conexión al guardar la cita.', 'danger');
            }
        },

        eventClick: function (info) {
            if (info.event.url) {
                info.jsEvent.preventDefault();
                openEditModal(info.event);
            }
        },

        eventContent: function (info) {
            const props = info.event.extendedProps;
            const card = document.createElement('div');
            card.className = 'calendar-event-card';

            [
                ['Motivo', props.reason],
                ['Mascota', props.petName],
                ['Tutor', props.tutor],
                ['Dirección', props.address]
            ].forEach(([label, value]) => {
                const line = document.createElement('div');
                line.className = 'calendar-event-line';
                line.textContent = `${label}: ${value || 'No indicado'}`;
                card.appendChild(line);
            });

            return { domNodes: [card] };
        },

        eventDidMount: function (info) {
            const tutor = info.event.extendedProps.tutor ? 'Tutor: ' + info.event.extendedProps.tutor : '';
            const reason = info.event.extendedProps.reason ? ' | Motivo: ' + info.event.extendedProps.reason : '';
            info.el.setAttribute('title', tutor + reason);
        }
    });

    calendar.render();

    window.addEventListener('resize', function () {
        const currentIsMobile = window.innerWidth < 768;
        if (currentIsMobile !== isMobile) {
            isMobile = currentIsMobile;
            calendar.changeView(isMobile ? 'listWeek' : 'dayGridMonth');
        }
    });
});

