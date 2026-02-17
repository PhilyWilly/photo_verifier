//const apiKey = localStorage.getItem('api_key'); // Disabled

async function submitPictures(e) {
    e.preventDefault();

    // Get inputs
    const ordernumber = document.getElementById('ordernumber').value;
    const retoure = document.getElementById('retoure').checked;
    const files = document.getElementById('images').files;

    // Check if every input is satisfied
    if ((!ordernumber && !retoure) || files.length === 0) {
        alert('Bitte Bestellungsnummer und mindestens ein Bild angeben.');
        return;
    }

    // Create FormData
    const formData = new FormData();
    if (!retoure) formData.append('number', ordernumber);
    else formData.append('number', 'retour!')
    formData.append('retoure', retoure);
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        // Send FormData
        const res = await fetch('/orders/', {
            method: 'POST',
            /*headers: {
                'X-API-Key': apiKey
            },*/
            body: formData
        });
        if (!res.ok) throw new Error('Error while uploading'); 
        const data = await res.json();
        clearFields();
    } catch (err) {
        alert('Fehler beim Hochladen der Bilder.');
    }
}

function clearFields() {
    document.getElementById('ordernumber').value = "";
    document.getElementById('images').value = "";
}

document.getElementById('orderForm').addEventListener('submit', submitPictures);