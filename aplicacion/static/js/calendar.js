/**
 * VETKI - Módulo de Agenda Clínica (FullCalendar v6)
 * Gestión responsive y adaptabilidad móvil.
 */

document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    let isMobile = window.innerWidth < 768;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: isMobile ? 'listWeek' : 'dayGridMonth',
        locale: 'es',
        firstDay: 1,
        timeZone: 'local',
        height: 'auto',

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

