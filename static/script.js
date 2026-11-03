
async function loadWeather() {

    const status = document.getElementById("status");

    status.textContent = "Loading NASA observations...";

    try {

        const response = await fetch("/api/weather");

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || "Unable to load data");
        }

        function display(id, value, unit = "") {

            document.getElementById(id).textContent =
                value === null || value === undefined
                ? "--"
                : value + unit;
        }

        display("temperature", data.temperature, " °C");
        display("ground-temperature", data.ground_temperature, " °C");
        display("wind-speed", data.wind_speed);
        display("pressure", data.pressure, " Pa");

        document.getElementById("observation-date").textContent =
            "Observation date: " +
            (data.observation_date || "Not provided") +
            (data.sol !== null && data.sol !== undefined
                ? " | Mars Sol: " + data.sol
                : "");

        status.textContent =
            "Latest available observation retrieved from NASA.";
        
    await loadHistory();

    } catch (error) {

        status.textContent = "Error: " + error.message;

        console.error(error);
    }
}
// Refresh when the user clicks the dashboard button.


let temperatureChart = null;

async function loadHistory() {

    try {

        const response = await fetch("/api/history");

        const records = await response.json();

        const validRecords = records.filter(
            item => item.temperature !== ""
            && item.temperature !== null
            && Number.isFinite(Number(item.temperature))
        );

        const labels = validRecords.map(
            item => item.sol || item.observation_date
        );

        const values = validRecords.map(
            item => Number(item.temperature)
        );

        const canvas = document.getElementById(
            "temperatureChart"
        );

        if (temperatureChart) {
            temperatureChart.destroy();
        }

        temperatureChart = new Chart(canvas, {

            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Temperature (°C)",

                    data: values,

                    borderWidth: 2,

                    tension: 0.3
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        title: {
                            display: true,
                            text: "Temperature (°C)"
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: "Mars Sol / Observation"
                        }
                    }
                }
            }
        });

    } catch (error) {

        console.error("Chart error:", error);

    }
}
loadWeather();
loadHistory();