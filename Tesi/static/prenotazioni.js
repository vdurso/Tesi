document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#prenotazioni-tabella tbody");

    // Fetch data from the API
    fetch("/lista_prenotazioni")
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
            // Populate the table
            data.forEach((prenotazione) => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${prenotazione.nome}</td>
                    <td>${prenotazione.cognome}</td>
                    <td>${prenotazione.email}</td>
                    <td>${prenotazione.telefono}</td>
                    <td>${prenotazione.persone}</td>
                    <td>${prenotazione.data}</td>
                    <td>${prenotazione.turno}</td>
                `;

                tableBody.appendChild(row);
            });
        })
        .catch((error) => {
            console.error("Errore durante il recupero delle prenotazioni:", error);
        });
});
