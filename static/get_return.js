//const apiKey = localStorage.getItem('api_key'); // Disabled
let currentSearch = "";
let offset = 0;
const limit = 10;

// Get all dates
async function getDates() {
    try {
        const res = await fetch('/retoure_dates/', {
            method: 'GET',
            /*headers: {
                'X-API-Key': apiKey
            }*/
        });
        if (!res.ok) throw new Error('Failed to fetch dates');
        const data = await res.json();

        createDateCollapsibles(data.dates);
    }
    catch (err) {
        console.error(err);
        const grid = document.getElementById('imagesGrid');
        grid.textContent = 'Es ist ein Fehler aufgetreten! Höchstwahrscheinlich wurden noch keine Retouren angelegt.';
    }
}

// Create collapsibles for each date
function createDateCollapsibles(dates) {
    const container = document.getElementById('retoure-container');
    dates.forEach(date => {
        // Create collapsible for each date
        const collapsible = document.createElement('div');
        collapsible.className = 'collapsible';

        // Create button for collapsible
        const collapsibleButton = document.createElement('button');
        collapsibleButton.className = 'collapsible-button';
        const heading = document.createElement('h3');
        heading.textContent = new Date(date).toLocaleDateString('de-DE');
        const collapsibleIcon = document.createElement('span');
        collapsibleIcon.className = 'collapsible-icon';
        collapsibleIcon.textContent = '+';
        collapsibleButton.appendChild(document.createElement('span')); // Spacer
        collapsibleButton.appendChild(heading);
        collapsibleButton.appendChild(collapsibleIcon);
        collapsibleButton.addEventListener('click', onCollapsiblePress);

        // Create container for collapsible content
        const collapsibleContainer = document.createElement('div');
        collapsibleContainer.className = 'collapsible-container';
        collapsibleContainer.style.display = 'none';
        collapsibleContainer.id = `collapsible-${new Date(date).toLocaleDateString('de-DE')}`;

        collapsible.appendChild(collapsibleButton);
        collapsible.appendChild(collapsibleContainer);
        container.appendChild(collapsible);
    });
}

// Sends the form data to the server
async function onCollapsiblePress(e) {
    e.preventDefault();
    const currentTarget = e.currentTarget;

    const date = currentTarget.querySelector('h3').innerText.trim();
    const container = document.getElementById('collapsible-' + date);
    container.innerHTML = '';
    try {
        // Collect imagepaths
        const parts = date.split('.');
        const day = parts[0].padStart(2, '0');
        const month = parts[1].padStart(2, '0');
        const year = parts[2];
        const dateStr = `${year}-${month}-${day}`;
        const res = await fetch(`/images_by_date/${encodeURIComponent(dateStr)}/`, {
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
                    img.style.width = '50%';
                    img.style.objectFit = 'cover';
                    container.appendChild(img);
                })
                .catch(() => {
                    container.textContent = `Folgende Bild konnte nicht geladen werden: ${filename}`;
                });
            });
        } else {
            container.textContent = 'Es wurden keine Bilder dieser Bestellnummer gemacht';
        }
    } catch (err) {
        console.error(err);
        if(err)
        container.textContent = 'Es ist ein Fehler aufgetreten! Höchstwahrscheinlich wurde diese Artikellnummer nicht angelegt.';
    }
    finally {
        const collapsed = container.style.display === 'none';
        container.style.display = collapsed ? 'block' : 'none';
        console.log(currentTarget);
        const icon = currentTarget.querySelector('.collapsible-icon');
        icon.textContent = collapsed ? '-' : '+';
        icon.style.fontSize = collapsed ? '2em' : '1.5em';
    }
}



// On page reload call function
window.addEventListener('DOMContentLoaded', getDates);
