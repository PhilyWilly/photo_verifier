//const apiKey = localStorage.getItem('api_key'); // Disabled
let currentSearch = "";
let offset = 0;
const limit = 10;

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
        const res = await fetch(`/images/?order_number=${encodeURIComponent(ordernumber)}`, {
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
            if(data.images.length > 1) {
                grid.style.width = "70vw";
            }
            else {
                grid.style.width = "";
            }
            });
        } else {
            grid.textContent = 'Es wurden keine Bilder dieser Bestellnummer gemacht';
        }
    } catch (err) {
        if(err)
        grid.textContent = 'Es ist ein Fehler aufgetreten! Höchstwahrscheinlich wurde diese Artikellnummer nicht angelegt.';
    }
}

// This creates the suggestions for the search bar
async function loadSuggestions(search = "", reset = true) {
    if (reset) offset = 0;
    currentSearch = search;
    const response = await fetch(`/order_numbers/?q=${encodeURIComponent(search)}&offset=${offset}&limit=${limit}`);
    if (!response.ok) return;
    const data = await response.json();
    const datalist = document.getElementById('suggestions');
    if (reset) datalist.innerHTML = '';
    data.order_numbers.forEach(order => {
        const option = document.createElement('option');
        option.value = order;
        datalist.appendChild(option);
    });
}

// On submit call function
document.getElementById('orderForm').addEventListener('submit', submitOrdernumberRequest);

// On page reload call function
window.addEventListener('DOMContentLoaded', loadSuggestions);

// Listen for input changes
document.getElementById('ordernumber').addEventListener('input', (e) => {
    loadSuggestions(e.target.value, true);
});