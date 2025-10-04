const token = localStorage.getItem("accessToken");

async function loadProfile() {
    const container = document.getElementById("profileContainer");

    try {
    const response = await fetch("http://127.0.0.1:8000/users/profile/", {
        method: "GET",
        headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}` // if JWT auth
        }
    });

    if (!response.ok) {
        throw new Error("Failed to fetch profile");
    }

    const data = await response.json();

    container.innerHTML = `
        <h2>${data.username}</h2>
        <p><strong>Email:</strong> ${data.email}</p>
        <p><strong>First Name:</strong> ${data.first_name}</p>
        <p><strong>Last Name:</strong> ${data.last_name}</p>
    `;
    } catch (error) {
    container.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}

loadProfile();

fetch('/templates/navbar.html')
    .then(response => {
        if (!response.ok) throw new Error("Failed to load navbar");
        return response.text();
    })
    .then(html => {
        document.getElementById('navbar-container').innerHTML = html;
    })
    .catch(error => console.error("Error loading navbar:", error));
