(() => {
    const vault = document.querySelector("[data-login-vault]");
    const form = document.querySelector(".auth-form");
    const button = document.querySelector("[data-login-submit]");
    const status = document.querySelector("[data-login-status]");
    const hasErrors = Boolean(document.querySelector(".auth-form .alert-danger"));
    const symbols = ["7", "★", "◆", "#", "✦", "✓"];

    if (vault && form && button && status) {
        if (hasErrors) {
            vault.classList.add("is-failed");
            status.textContent = "Доступ не підтверджено";
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            vault.classList.remove("is-failed");
            vault.classList.add("is-spinning");
            status.textContent = "Перевірка коду...";
            button.disabled = true;

            const wheels = [...vault.querySelectorAll(".login-vault__wheel")];
            let step = 0;
            const spinTimer = window.setInterval(() => {
                wheels.forEach((wheel, index) => {
                    wheel.textContent = symbols[(step + index * 2) % (symbols.length - 1)];
                });
                step += 1;
            }, 110);

            try {
                const response = await Promise.all([
                    fetch(form.action || window.location.href, {
                        body: new FormData(form),
                        credentials: "same-origin",
                        headers: { "X-Requested-With": "XMLHttpRequest" },
                        method: "POST",
                    }),
                    new Promise((resolve) => window.setTimeout(resolve, 1320)),
                ]).then(([result]) => result);

                window.clearInterval(spinTimer);
                vault.classList.remove("is-spinning");

                if (response.redirected) {
                    wheels.forEach((wheel) => {
                        wheel.textContent = "✓";
                    });
                    vault.classList.add("is-success");
                    status.textContent = "Код підтверджено";
                    sessionStorage.setItem("login-pending", "1");
                    window.setTimeout(() => window.location.assign(response.url), 450);
                    return;
                }

                wheels.forEach((wheel) => {
                    wheel.textContent = "✕";
                });
                vault.classList.add("is-failed");
                status.textContent = "Доступ не підтверджено";
                button.disabled = false;

                const responseHtml = await response.text();
                window.setTimeout(() => {
                    document.open();
                    document.write(responseHtml);
                    document.close();
                }, 350);
            } catch (error) {
                window.clearInterval(spinTimer);
                vault.classList.remove("is-spinning");
                vault.classList.add("is-failed");
                status.textContent = "Не вдалося перевірити доступ";
                button.disabled = false;
            }
        });
    }

    if (sessionStorage.getItem("login-pending") === "1" && window.location.pathname === "/") {
        sessionStorage.removeItem("login-pending");

        const successNotice = document.createElement("div");
        successNotice.className = "login-success-notice";
        successNotice.setAttribute("role", "status");
        successNotice.innerHTML = "<strong>Доступ підтверджено</strong><span>Вітаємо в порталі</span>";
        document.body.appendChild(successNotice);

        window.setTimeout(() => successNotice.remove(), 2600);
    }
})();
