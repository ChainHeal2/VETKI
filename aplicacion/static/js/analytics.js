/**
 * VETKI - Módulo de Analítica y Gráficos (Chart.js)
 * Carga de indicadores y renderizado de gráficos epidemiológicos.
 */

document.addEventListener("DOMContentLoaded", async () => {
    const status = document.getElementById("diseaseStatus");
    const cardsContainer = document.getElementById("diseaseCards");
    const sourceBadge = document.getElementById("sourceBadge");

    if (!cardsContainer) return;

    try {
        const fetchUrl = cardsContainer.dataset.analyticsUrl || "/analytics/diseases";
        const response = await fetch(fetchUrl, {
            headers: { "Accept": "application/json" }
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error || `Error del servidor (${response.status})`);
        }

        const payload = await response.json();
        if (!payload || !Array.isArray(payload.diseases)) {
            throw new Error("Formato de datos no válido.");
        }

        if (payload.source && sourceBadge) {
            sourceBadge.textContent = `Fuente: ${payload.source}`;
        }

        const diseases = payload.diseases;

        // Renderizado dinámico de tarjetas de resumen
        cardsContainer.innerHTML = diseases.map(d => {
            const isUp = d.variation_percent > 0;
            const isDown = d.variation_percent < 0;
            const symbol = isUp ? "↑" : isDown ? "↓" : "=";
            const badgeBg = isUp ? "bg-danger-subtle text-danger" : isDown ? "bg-success-subtle text-success" : "bg-secondary-subtle text-secondary";

            return `
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card h-100 border-0 bg-body-tertiary p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold text-body-emphasis small">${d.disease}</span>
                        <span class="badge ${badgeBg} fw-semibold">${symbol} ${Math.abs(d.variation_percent)}%</span>
                    </div>
                    <div class="d-flex align-items-baseline gap-2">
                        <span class="fs-2 fw-bold text-body-emphasis">${d.current_cases}</span>
                        <span class="small text-body-secondary">casos actuales</span>
                    </div>
                    <span class="small text-body-secondary mt-1">Previo: ${d.previous_cases} casos</span>
                </div>
            </div>`;
        }).join("");

        if (window.chartJsLoadError || typeof Chart === "undefined") {
            if (status) status.textContent = "Indicadores cargados (Gráfico no disponible).";
            return;
        }

        const ctx = document.getElementById("diseaseChart");
        if (ctx) {
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: diseases.map(d => d.disease),
                    datasets: [
                        {
                            label: "Últimos 30 días",
                            data: diseases.map(d => d.current_cases),
                            backgroundColor: "rgba(13, 110, 253, 0.85)",
                            borderColor: "#0d6efd",
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: "Período Anterior",
                            data: diseases.map(d => d.previous_cases),
                            backgroundColor: "rgba(108, 117, 125, 0.4)",
                            borderColor: "#6c757d",
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                boxWidth: 12,
                                font: { size: 12 },
                                color: "#dee2e6"
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return ` ${context.dataset.label}: ${context.raw} casos`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                color: "#adb5bd"
                            },
                            title: {
                                display: true,
                                text: "Nº de Casos",
                                color: "#adb5bd"
                            },
                            grid: { color: "rgba(255, 255, 255, 0.05)" }
                        },
                        x: {
                            ticks: { color: "#adb5bd" },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        if (status) {
            status.textContent = diseases.every(d => d.current_cases === 0 && d.previous_cases === 0)
                ? "No se registran casos recientes en el boletín epidemiológico."
                : "Monitoreo epidemiológico consolidado de los últimos 30 días.";
        }

    } catch (error) {
        if (status) {
            status.textContent = error.message || "No se pudieron cargar los indicadores epidemiológicos.";
        }
    }
});

