document.addEventListener('DOMContentLoaded', () => {
    const locationSearch = document.getElementById('locationSearch');
    const searchResults = document.getElementById('searchResults');
    const weatherDisplay = document.getElementById('weatherDisplay');
    const loading = document.getElementById('loading');

    let searchTimeout = null;

    // Search input handler
    locationSearch.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(searchTimeout);

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        searchTimeout = setTimeout(() => {
            fetchLocations(query);
        }, 300);
    });

    async function fetchLocations(query) {
        try {
            const response = await fetch(`/api/v1/weather/search?name=${encodeURIComponent(query)}`);
            const data = await response.json();
            displaySearchResults(data);
        } catch (err) {
            console.error('Search failed:', err);
        }
    }

    function displaySearchResults(results) {
        searchResults.innerHTML = '';
        if (results.length === 0) {
            searchResults.classList.add('hidden');
            return;
        }

        results.forEach(loc => {
            const div = document.createElement('div');
            div.className = 'result-item';
            div.innerHTML = `
                <span class="loc-name">${loc.name}</span>
                <span class="loc-meta">${loc.region ? loc.region + ', ' : ''}${loc.country} (${loc.lat.toFixed(2)}, ${loc.lon.toFixed(2)})</span>
            `;
            div.onclick = () => selectLocation(loc);
            searchResults.appendChild(div);
        });
        searchResults.classList.remove('hidden');
    }

    async function selectLocation(loc) {
        locationSearch.value = loc.name;
        searchResults.classList.add('hidden');
        showLoading(true);
        weatherDisplay.classList.add('hidden');

        try {
            // Fetch Current Weather
            const currentRes = await fetch(`/api/v1/weather/current?lat=${loc.lat}&lon=${loc.lon}`);
            if (!currentRes.ok) throw new Error('Failed to fetch current weather');
            const currentData = await currentRes.json();

            // Fetch Daily Averages
            const dailyRes = await fetch(`/api/v1/weather/daily-average?lat=${loc.lat}&lon=${loc.lon}`);
            const dailyData = await dailyRes.json();

            // Fetch Deviation for today
            const today = new Date().toISOString().split('T')[0];
            const devRes = await fetch(`/api/v1/weather/source-deviation?date=${today}&lat=${loc.lat}&lon=${loc.lon}`);
            const devData = await devRes.json();

            updateUI(loc, currentData, dailyData, devData);
        } catch (err) {
            alert('Error loading data: ' + err.message);
        } finally {
            showLoading(false);
        }
    }

    function updateUI(loc, current, daily, deviation) {
        // Summary
        document.getElementById('cityName').textContent = loc.name;
        document.getElementById('coordinates').textContent = `${loc.lat.toFixed(2)}, ${loc.lon.toFixed(2)}`;

        // Use weighted consensus if available, fallback to average
        const mainVal = current.weighted_temperature !== null ? current.weighted_temperature : current.average_temperature;
        document.getElementById('mainTemp').textContent = mainVal.toFixed(1);

        // Sources
        const sourcesList = document.getElementById('sourcesList');
        sourcesList.innerHTML = current.sources.map(s => `
            <div class="source-item">
                <span class="source-name">${s.source}</span>
                <span class="source-temp">${s.temperature.toFixed(1)}°C</span>
            </div>
        `).join('');

        // Deviation
        const devDisplay = document.getElementById('deviationDisplay');
        if (deviation.deviation_yr_vs_openmeteo !== null) {
            const dev = deviation.deviation_yr_vs_openmeteo.toFixed(2);
            devDisplay.innerHTML = `
                <div class="meta-item">
                    <label>YR vs Open-Meteo</label>
                    <span style="font-size: 1.5rem; color: var(--primary)">${dev}°C Offset</span>
                </div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 10px;">
                    Calculated for ${deviation.date}
                </p>
            `;
        } else {
            devDisplay.innerHTML = '<p class="loc-meta">Insufficient data for source comparison.</p>';
        }

        // Daily
        const dailyList = document.getElementById('dailyList');
        dailyList.innerHTML = daily.slice(0, 5).map(d => `
            <div class="daily-item">
                <span class="daily-date">${d.date}</span>
                <span class="daily-temp">${Math.round(d.average_temperature)}°C</span>
            </div>
        `).join('');

        weatherDisplay.classList.remove('hidden');
    }

    function showLoading(show) {
        loading.classList.toggle('hidden', !show);
    }
});
