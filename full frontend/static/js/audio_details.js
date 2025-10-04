async function getData(url) {
    const accessToken = localStorage.getItem("accessToken");  

    if (!accessToken) {
        console.error("No access token found in localStorage");
        return;
    }

    try {
        const response = await fetch(url, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
            "Content-Type": "application/json"
            }
        });   
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        } 
        const result = await response.json();

        console.log(result)
    } catch (error) {
        console.error("Error:", error.message);
    }
}
getData("http://127.0.0.1:8000/stt/audio/11/")