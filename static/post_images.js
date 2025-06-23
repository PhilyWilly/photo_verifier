const apiKey = localStorage.getItem('api_key');

async function submitPictures(e) {
    e.preventDefault();

    // Get inputs
    const ordernumber = document.getElementById('ordernumber').value;
    const files = document.getElementById('images').files;

    // Check if every input is satisfied
    if (!ordernumber || files.length === 0) {
        alert('Bitte Bestellungsnummer und mindestens ein Bild angeben.');
        return;
    }

    // Create FormData
    const formData = new FormData();
    formData.append('number', ordernumber);
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        // Send FormData
        const res = await fetch('/orders/', {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey
            },
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