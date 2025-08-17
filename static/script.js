document.addEventListener('DOMContentLoaded', () => {

    // --- DOM Element References ---
    const generateBtn = document.getElementById('generateBtn');
    const lengthInput = document.getElementById('length');
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    const levelsInput = document.getElementById('working_levels');
    const ladderCheckbox = document.getElementById('include_ladder'); // New checkbox
    
    const resultsContainer = document.getElementById('results-container');
    const summaryDiv = document.getElementById('summary');
    const tableBody = document.querySelector('#results-table tbody');
    const loader = document.getElementById('loader');
    const errorMessageDiv = document.getElementById('error-message');
    
    const printBtn = document.getElementById('printBtn');
    const savePdfBtn = document.getElementById('savePdfBtn');
    const emailBtn = document.getElementById('emailBtn');
    const whatsappBtn = document.getElementById('whatsappBtn');


    // --- Event Listeners ---
    generateBtn.addEventListener('click', async () => {
        resultsContainer.style.display = 'none';
        errorMessageDiv.style.display = 'none';
        loader.style.display = 'block';

        // Collect all data, including the checkbox state
        const data = {
            scaffold_type: 'facade', // Type is now fixed
            length: lengthInput.value,
            width: widthInput.value,
            height: heightInput.value,
            working_levels: levelsInput.value,
            include_ladder: ladderCheckbox.checked // Send true/false
        };

        if (!data.length || !data.width || !data.height || !data.working_levels) {
            showError('All dimension fields are required.');
            return;
        }

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`Server responded with an error: ${response.status}`);
            const result = await response.json();
            displayResults(result);
        } catch (error) {
            showError(`Failed to get results. Error: ${error.message}`);
        } finally {
            loader.style.display = 'none';
        }
    });
    
    printBtn.addEventListener('click', () => window.print());
    savePdfBtn.addEventListener('click', saveAsPDF);
    emailBtn.addEventListener('click', shareByEmail);
    whatsappBtn.addEventListener('click', shareByWhatsApp);


    // --- UI and Action Functions (displayResults is updated) ---
    function displayResults(data) {
        const { summary, materials } = data;
        summaryDiv.innerHTML = `<strong>${summary['Scaffold Type']}</strong><br>`;
        for (const [key, value] of Object.entries(summary)) {
            if (key !== 'Scaffold Type') {
                summaryDiv.innerHTML += `- ${key}: ${value}<br>`;
            }
        }

        tableBody.innerHTML = '';
        for (const [item, quantity] of Object.entries(materials)) {
            // Special handling for the separator
            if (item.includes('---')) {
                tableBody.innerHTML += `<tr class="separator"><td colspan="2">${item}</td></tr>`;
            } else {
                tableBody.innerHTML += `<tr><td>${item}</td><td>${quantity}</td></tr>`;
            }
        }
        resultsContainer.style.display = 'block';
    }
    
    // ... all other functions (showError, getShareableText, saveAsPDF etc.) remain the same ...

});