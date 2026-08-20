const API_KEY = "TA_CLE_API";   // ← mets ta clé ici

async function getWeather() {
    const city = document.getElementById("city").value.trim();
    if (!city) return;

    try {
        // Météo actuelle
        const res = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=metric&lang=fr`
        );
        const data = await res.json();
        if (data.cod !== 200) throw new Error(data.message);

        document.getElementById("weather").innerHTML = `
            <h2>${data.name}, ${data.sys.country}</h2>
            <div class="temp">${Math.round(data.main.temp)}°C</div>
            <div class="desc">${data.weather[0].description}</div>
            <div class="details">
                <div class="detail"><div>Ressenti</div><strong>${Math.round(data.main.feels_like)}°C</strong></div>
                <div class="detail"><div>Humidité</div><strong>${data.main.humidity}%</strong></div>
                <div class="detail"><div>Vent</div><strong>${data.wind.speed} m/s</strong></div>
                <div class="detail"><div>Pression</div><strong>${data.main.pressure} hPa</strong></div>
            </div>
        `;

        // Prévisions 5 jours
        const resF = await fetch(
            `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=metric&lang=fr`
        );
        const forecast = await resF.json();

        // On prend un point par jour (midi)
        const daily = {};
        forecast.list.forEach(item => {
            const date = item.dt_txt.split(" ")[0];
            if (!daily[date] && item.dt_txt.includes("12:00:00")) {
                daily[date] = item;
            }
        });

        let html = "";
        Object.values(daily).slice(0, 5).forEach(day => {
            const d = new Date(day.dt * 1000);
            html += `
                <div class="day">
                    <div>${d.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric" })}</div>
                    <img src="https://openweathermap.org/img/wn/${day.weather[0].icon}@2x.png" alt="">
                    <div><strong>${Math.round(day.main.temp)}°C</strong></div>
                    <div style="font-size:0.9em">${day.weather[0].description}</div>
                </div>
            `;
        });
        document.getElementById("forecast").innerHTML = html;

    } catch (err) {
        document.getElementById("weather").innerHTML = `<p style="color:#ff8a80">Erreur : ${err.message}</p>`;
        document.getElementById("forecast").innerHTML = "";
    }
}

// Charge Paris au démarrage
getWeather();
