/**
 * VETKI - Módulo de Agenda Clínica (FullCalendar v6)
 * Gestión responsive y adaptabilidad móvil.
 */

document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    const calendarContainer = document.getElementById('appointmentCalendar');
    const messageEl = document.getElementById('calendarMessage');

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

    let isMobile = window.innerWidth < 768;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: isMobile ? 'listWeek' : 'dayGridMonth',
        locale: 'es',
        firstDay: 1,
        timeZone: 'local',
        height: 'auto',
        // Permite mover las citas dentro del calendario; por ahora el cambio
        // solo vive en la vista y no se guarda en el servidor.
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
                window.location.href = info.event.url;
                info.jsEvent.preventDefault();
            }
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

