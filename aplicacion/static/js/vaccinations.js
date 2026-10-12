/**
 * VETKI - Módulo de Gestión de Vacunaciones (Modal Interactivo)
 * Consumo de endpoints REST /api/vaccinations/... con paginación y estados.
 */

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("vaccinationModal");
    if (!modal) return;

    const form = document.getElementById("vaccinationForm");
    const history = document.getElementById("vaccinationHistory");
    const status = document.getElementById("vaccinationStatus");
    const vaccinationIdInput = document.getElementById("vaccinationId");
    const saveButton = document.getElementById("saveVaccination");
    const cancelButton = document.getElementById("cancelVaccinationEdit");
    const historyTab = document.getElementById("history-tab");
    const formTab = document.getElementById("new-tab");
    const pagination = document.getElementById("vaccinationPagination");
    const pageInfo = document.getElementById("vaccinationPageInfo");
    const previousPageButton = document.getElementById("previousVaccinationPage");
    const nextPageButton = document.getElementById("nextVaccinationPage");
    const pageSize = 5;

    let petId;
    let vaccinations = [];
    let currentPage = 1;

    function setStatus(message, type = "info") {
        if (!status) return;
        status.className = `small mt-3 text-${type}`;
        status.textContent = message;
    }

    function showTab(tab) {
        if (window.bootstrap && bootstrap.Tab && tab) {
            bootstrap.Tab.getOrCreateInstance(tab).show();
        }
    }

    function resetForm() {
        if (!form) return;
        form.reset();
        if (vaccinationIdInput) vaccinationIdInput.value = "";
        if (saveButton) saveButton.textContent = "Guardar vacuna";
        if (cancelButton) cancelButton.hidden = true;
    }

    function addCell(row, value) {
        const cell = document.createElement("td");
        cell.textContent = value || "—";
        row.appendChild(cell);
    }

    function renderHistory() {
        if (!history) return;
        history.replaceChildren();

        const pageCount = Math.max(1, Math.ceil(vaccinations.length / pageSize));
        currentPage = Math.min(currentPage, pageCount);
        if (pagination) pagination.hidden = pageCount <= 1;
        if (previousPageButton) previousPageButton.disabled = currentPage === 1;
        if (nextPageButton) nextPageButton.disabled = currentPage === pageCount;
        if (pageInfo) pageInfo.textContent = `Página ${currentPage} de ${pageCount}`;

        if (vaccinations.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 5;
            cell.className = "text-center py-3";
            cell.textContent = "Sin registros de vacunación.";
            row.appendChild(cell);
            history.appendChild(row);
            return;
        }

        const startIndex = (currentPage - 1) * pageSize;
        const pageVaccinations = vaccinations.slice(startIndex, startIndex + pageSize);

        pageVaccinations.forEach(vaccination => {
            const row = document.createElement("tr");
            addCell(row, vaccination.vaccine_name);
            addCell(row, vaccination.application_date);
            addCell(row, vaccination.lot_number);
            addCell(row, vaccination.veterinarian_notes);

            const actions = document.createElement("td");
            actions.className = "text-nowrap";

            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.className = "btn btn-outline-light btn-sm me-1";
            editButton.dataset.action = "edit";
            editButton.dataset.id = vaccination.id;
            editButton.textContent = "Editar";

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "btn btn-outline-danger btn-sm";
            deleteButton.dataset.action = "delete";
            deleteButton.dataset.id = vaccination.id;
            deleteButton.textContent = "Eliminar";

            actions.append(editButton, deleteButton);
            row.appendChild(actions);
            history.appendChild(row);
        });
    }

    async function loadHistory() {
        try {
            const response = await fetch(`/api/vaccinations/${petId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "No se pudo cargar el historial.");
            }

            vaccinations = data.vaccinations || [];
            renderHistory();
        } catch (error) {
            if (pagination) pagination.hidden = true;
            if (history) {
                history.replaceChildren();
                const row = document.createElement("tr");
                const cell = document.createElement("td");
                cell.colSpan = 5;
                cell.className = "text-center text-danger py-3";
                cell.textContent = error.message;
                row.appendChild(cell);
                history.appendChild(row);
            }
        }
    }

    if (previousPageButton) {
        previousPageButton.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage -= 1;
                renderHistory();
            }
        });
    }

    if (nextPageButton) {
        nextPageButton.addEventListener("click", () => {
            const pageCount = Math.ceil(vaccinations.length / pageSize);
            if (currentPage < pageCount) {
                currentPage += 1;
                renderHistory();
            }
        });
    }

    modal.addEventListener("show.bs.modal", event => {
        const button = event.relatedTarget;
        if (!button) return;
        petId = button.dataset.petId;

        const nameEl = document.getElementById("vaccinationPetName");
        if (nameEl) nameEl.textContent = button.dataset.petName || "";

        currentPage = 1;
        resetForm();
        setStatus("");
        showTab(historyTab);
        loadHistory();
    });

    if (history) {
        history.addEventListener("click", async event => {
            const button = event.target.closest("button[data-action]");
            if (!button) return;

            const vaccinationId = button.dataset.id;
            const url = `/api/vaccinations/${petId}/${vaccinationId}`;

            if (button.dataset.action === "edit") {
                try {
                    const response = await fetch(url);
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "No se pudo abrir la vacuna.");
                    }

                    const vaccination = data.vaccination;
                    form.elements.vaccine_name.value = vaccination.vaccine_name || "";
                    form.elements.lot_number.value = vaccination.lot_number || "";
                    form.elements.veterinarian_notes.value = vaccination.veterinarian_notes || "";

                    vaccinationIdInput.value = vaccination.id;
                    saveButton.textContent = "Actualizar vacuna";
                    cancelButton.hidden = false;
                    setStatus("");
                    showTab(formTab);
                } catch (error) {
                    setStatus(error.message, "danger");
                }
                return;
            }

            if (button.dataset.action === "delete") {
                if (!window.confirm("¿Quieres eliminar esta vacuna?")) return;

                const csrfToken = form.querySelector('input[name="csrf_token"]')?.value || "";

                try {
                    const response = await fetch(url, {
                        method: "DELETE",
                        headers: { "X-CSRFToken": csrfToken }
                    });

                    if (!response.ok) {
                        const data = await response.json();
                        throw new Error(data.error || "No se pudo eliminar la vacuna.");
                    }

                    setStatus("Vacuna eliminada.", "success");
                    await loadHistory();
                } catch (error) {
                    setStatus(error.message, "danger");
                }
            }
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener("click", () => {
            resetForm();
            setStatus("");
        });
    }

    if (form) {
        form.addEventListener("submit", async event => {
            event.preventDefault();

            const vaccinationId = vaccinationIdInput.value;
            const csrfToken = form.querySelector('input[name="csrf_token"]')?.value || "";
            const payload = {
                vaccine_name: form.elements.vaccine_name.value.trim(),
                lot_number: form.elements.lot_number.value.trim() || null,
                veterinarian_notes: form.elements.veterinarian_notes.value.trim() || null
            };

            const url = vaccinationId
                ? `/api/vaccinations/${petId}/${vaccinationId}`
                : `/api/vaccinations/${petId}`;

            try {
                const response = await fetch(url, {
                    method: vaccinationId ? "PUT" : "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "No se pudo guardar la vacuna.");
                }

                setStatus(
                    vaccinationId ? "Vacuna actualizada." : "Vacuna guardada.",
                    "success"
                );
                resetForm();
                currentPage = 1;
                await loadHistory();
                showTab(historyTab);
            } catch (error) {
                setStatus(error.message || "Error de conexión con el servidor.", "danger");
            }
        });
    }
});

