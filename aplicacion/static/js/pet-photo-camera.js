document.addEventListener("DOMContentLoaded", () => {
    const previewModalElement = document.getElementById("petPhotoPreviewModal");
    const previewModalImage = document.getElementById("petPhotoPreviewImage");
    const previewModalTitle = document.getElementById("petPhotoPreviewTitle");

    document.querySelectorAll("[data-pet-photo-trigger]").forEach((button) => {
        const input = document.getElementById(button.dataset.petPhotoTrigger);
        const preview = button.querySelector(".pet-photo-preview");
        const placeholder = button.querySelector(".pet-photo-placeholder");
        const status = button.parentElement.querySelector(".pet-photo-status");
        const cameraButton = button.parentElement.querySelector("[data-pet-photo-camera]");
        let previewUrl = null;

        if (!input || !preview || !placeholder) return;

        let savedPhotoUrl = preview.getAttribute("src");
        let hasSavedPhoto = preview.dataset.saved === "true";
        placeholder.hidden = hasSavedPhoto;

        const openCamera = () => {
            input.value = "";
            input.click();
        };

        button.addEventListener("click", () => {
            if (!hasSavedPhoto) {
                openCamera();
                return;
            }

            previewModalImage.src = savedPhotoUrl;
            previewModalTitle.textContent = `Fotografía de ${button.dataset.petName}`;
            bootstrap.Modal.getOrCreateInstance(previewModalElement).show();
        });

        cameraButton?.addEventListener("click", openCamera);

        input.addEventListener("change", async () => {
            const photo = input.files?.[0];
            if (!photo) return;

            if (previewUrl) URL.revokeObjectURL(previewUrl);
            previewUrl = URL.createObjectURL(photo);
            preview.src = previewUrl;
            preview.style.display = "block";
            placeholder.hidden = true;
            if (status) {
                status.hidden = false;
                status.textContent = "Guardando fotografía…";
            }

            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            const formData = new FormData();
            formData.append("photo", photo);

            try {
                const response = await fetch(button.dataset.uploadUrl, {
                    method: "POST",
                    headers: csrfToken ? { "X-CSRFToken": csrfToken } : {},
                    body: formData,
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(result.error || `Error HTTP ${response.status} al guardar la fotografía.`);
                }

                preview.dataset.saved = "true";
                preview.src = `${button.dataset.uploadUrl}?v=${Date.now()}`;
                savedPhotoUrl = preview.src;
                hasSavedPhoto = true;
                button.setAttribute("aria-label", `Ver fotografía de ${button.dataset.petName}`);
                button.title = "Ver fotografía";
                if (cameraButton) cameraButton.hidden = false;
                if (status) status.textContent = "Fotografía guardada.";
            } catch (error) {
                if (hasSavedPhoto && savedPhotoUrl) {
                    preview.src = savedPhotoUrl;
                    preview.style.display = "block";
                    placeholder.hidden = true;
                } else {
                    preview.removeAttribute("src");
                    preview.style.display = "none";
                    placeholder.hidden = false;
                }
                if (status) status.textContent = error.message;
            }
        });

        window.addEventListener("beforeunload", () => {
            if (previewUrl) URL.revokeObjectURL(previewUrl);
        });
    });
});
