// /static/js/navbar.js

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("navbar-container");
    if (!container) return;

    try {
        const response = await fetch("/templates/navbar.html");
        if (!response.ok) throw new Error("Navbar not found");

        const navbarHTML = await response.text();
        container.innerHTML = navbarHTML;

        const loginSignupContainer = container.querySelector(".login_signup_links");
        const token = localStorage.getItem("accessToken");

        if (token) {
            loginSignupContainer.innerHTML = `
                <a href="#" class="nav-link" id="logout-link">Logout</a>
                <a href="/templates/users/profile.html" id="ProfileButton"></a>
            `;

            const logoutLink = document.getElementById("logout-link");
            logoutLink.addEventListener("click", (e) => {
                e.preventDefault();
                localStorage.removeItem("accessToken");
                window.location.href = "/templates/stt.html";
            });
        }
    } catch (err) {
        console.error("Error loading navbar:", err);
    }
});
