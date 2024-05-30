const addRowButton = document.getElementById('addRowButton');
const dataBody = document.getElementById('dataBody');
const downloadButton = document.getElementById('downloadButton');

let fetchingInProgress = false; // Flag to prevent concurrent fetching

addRowButton.addEventListener('click', () => {
    const url = urlInput.value.trim(); 

    if (url && !fetchingInProgress) {
        fetchDataAndPopulateRow(url); 
        urlInput.value = ''; 
    }
});

async function fetchDataAndPopulateRow(url) { // Accept the URL as an argument
    fetchingInProgress = true;
    try {
        const response = await fetch('/fetch_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url }) // Use the passed URL
        });

        const result = await response.json();
        if(!response.ok){alert("Failed to fetch data. Redfin might be rate limiting or the property page has changed. Please try again later.");
    }
        if (response.ok) {
            const data = result.data;
            if (!data) { 
                // Data is null, indicating a scraping error
                alert("Failed to fetch data. Redfin might be rate limiting or the property page has changed. Please try again later.");
            } else{
            const newRow = dataBody.insertRow(0);
            for (let i = 0; i < 22; i++) { // Create 22 cells (including URL cell)
                newRow.insertCell();
            }
            newRow.cells[0].textContent = data['URL'];
            newRow.cells[1].textContent = data['Street Address'];
            newRow.cells[2].textContent = data['City'];
            newRow.cells[3].textContent = data['State'];
            newRow.cells[4].textContent = data['Postal Code'];
            newRow.cells[5].textContent = data['Price'];
            newRow.cells[6].textContent = data['Bed Room'];
            newRow.cells[7].textContent = data['Bath Room'];
            newRow.cells[8].textContent = data['Sq.Ft.'];
            newRow.cells[9].textContent = data['House type'];
            newRow.cells[10].textContent = data['Built Year'];
            newRow.cells[11].textContent = data['Area'];
            newRow.cells[12].textContent = data['Price/Sq.Ft'];
            newRow.cells[13].textContent = data['Car Parking'];
            newRow.cells[14].textContent = data['AC'];
            newRow.cells[15].textContent = data['Agent Name'];
            newRow.cells[16].textContent = data['Brokerage'];
            newRow.cells[17].textContent = data['MLS ID'];
            newRow.cells[18].textContent = data['Time on Redfin'];
            newRow.cells[19].textContent = data["Buyer's Agent Commission"];
            newRow.cells[20].textContent = data["Agent License"];
            newRow.cells[21].textContent = data['Contact'];
            // Wait for 5 seconds before allowing the next fetch
            await new Promise(resolve => setTimeout(resolve, 5000));
        } 
        } else {
            console.error('Error fetching data:', result.error);
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        fetchingInProgress = false; // Allow next fetch
    }
}

downloadButton.addEventListener('click', () => {
    try {
        // Trigger the download
        window.location.href = '/download_excel';
    } catch (error) {
        console.error('Error initiating Excel download:', error);
        // You can display an error message to the user here
    }
});