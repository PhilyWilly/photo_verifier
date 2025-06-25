//const apiKey = localStorage.getItem('api_key'); // Disabled

// Sends the form data to the server
async function submitOrdernumberRequest(e) {
    e.preventDefault();

    // Collect html objects
    const ordernumber = document.getElementById('ordernumber').value.trim();
    const grid = document.getElementById('imagesGrid');
    grid.innerHTML = '';
    if (!ordernumber) return;

    try {
        // Collect imagepaths
        const res = await fetch(`/images/${ordernumber}/`, {
            method: 'GET',
            /*headers: {
                'X-API-Key': apiKey
            }*/
        });
        if (!res.ok) throw new Error('Order not found');
        const data = await res.json();

        if (data.images && data.images.length > 0) {
            // Collect the acctual images
            data.images.forEach(filename => {
                const img = document.createElement('img');
                // Fetch the image as a blob with the API key header
                fetch(`/image/${filename}/`, {
                    method: 'GET',
                    /*headers: {
                        'X-API-Key': apiKey
                    }*/
                })
                .then(response => {
                    if (!response.ok) throw new Error('Image not found');
                    return response.blob();
                })
                .then(blob => {
                    img.src = URL.createObjectURL(blob);
                    img.alt = filename;
                    img.style.width = '100%';
                    img.style.objectFit = 'cover';
                    grid.appendChild(img);
                })
                .catch(() => {
                    grid.textContent = `Folgende Bild konnte nicht geladen werden: ${filename}`;
                });
            });
        } else {
            grid.textContent = 'Es wurden keine Bilder dieser Bestellnummer gemacht';
        }
    } catch (err) {
        if(err)
        grid.textContent = 'Es ist ein Fehler aufgetreten!';
    }
}

// This creates the suggestions for the search bar
async function loadSuggestions() {
    try {
        // Get all order numbers
        const response = await fetch('/all_order_numbers/', {
            method: 'GET',
            /*headers: {
                'X-API-Key': apiKey
            }*/
        });
        if (!response.ok) throw new Error("Network response was not ok");
        
        // Prepare for incoming data
        const orderNumbers = await response.json(); 
        const datalist = document.getElementById('suggestions');
        datalist.innerHTML = ''; // Clear existing options
        
        orderNumbers.forEach(order => {
            // Create an option element
            const option = document.createElement('option');
            option.value = order;
            datalist.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

// On submit call function
document.getElementById('orderForm').addEventListener('submit', submitOrdernumberRequest);

// On page reload call function
window.addEventListener('DOMContentLoaded', loadSuggestions);