document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#tabella-prenotazioni tbody");

    fetch("/tutte_le_prenotazioni")
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
            data.forEach((prenotazione) => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${prenotazione.id}</td>
                    <td>${prenotazione.nome}</td>
                    <td>${prenotazione.cognome}</td>
                    <td>${prenotazione.email}</td>
                    <td>${prenotazione.telefono}</td>
                    <td>${prenotazione.persone}</td>
                    <td>${prenotazione.data}</td>
                    <td>${prenotazione.turno}</td>
                    <td>${prenotazione.tavoli.join(", ")}</td>
                    <td><button class="modifica-btn" data-id="${prenotazione.id}"> Modifica </button>
                    <button class="elimina-btn" data-id="${prenotazione.id}">Elimina</button>
                    </td>
                `;

                tableBody.appendChild(row);
            });
            modificaPrenotazione();
            eliminaPrenotazione();
        })
        .catch((error) => {
            console.error("Errore durante il recupero delle prenotazioni:", error);
        });
});

function eliminaPrenotazione(){
    document.querySelectorAll(".elimina-btn").forEach((button)=>{
        button.addEventListener('click',(event)=>{
            const id = event.target.dataset.id;

            if(confirm("Sei sicuro di voler eliminare questa prenotazione?")) {
                //richiama la route Flask passandogli il parametro id della prenotazione selezionata
                fetch(`/script_elimina/${id}`, {method:"DELETE"})
                .then((response)=>{
                    if(response.ok){
                        alert("Prenotazione eliminata con successo.")
                        location.reload();
                    }else{
                        return response.json().then((data)=> {
                            alert(data.error || "Errore durante l'eliminazione della prenotazione.")
                        })
                    }
                })
                .catch((error)=>{
                    console.error("Errore durante l'eliminazione:",error)
                    alert("Si è verificato un errore durante la prenotazione")
                })
            }
        })
    })

}

function modificaPrenotazione() {
    document.querySelectorAll(".modifica-btn").forEach((button) => {
        button.addEventListener("click", (event) => {
            const id = event.target.dataset.id;
            button.disabled= true
            // Crea una finestra pop-up per la modifica
            const popup = document.createElement("div");
            popup.classList.add("popup");
            popup.innerHTML = `
                <div class="popup-content">
                    <h2>Modifica Prenotazione</h2>
                    <form id="modifica-form">
                        <label for="persone">Numero di Persone:</label>
                        <input type="number" id="persone" name="persone" required>

                        <label for="data">Data:</label>
                        <input type="date" id="data" name="data" required>

                        <label for="turno">Turno:</label>
                        <select id="turno" name="turno" required>
                            <option value="pranzo">Pranzo</option>
                            <option value="cena">Cena</option>
                        </select>

                        <button type="submit">Salva</button>
                        <button type="button" id="chiudi-popup">Chiudi</button>
                    </form>
                </div>
            `;

            document.body.appendChild(popup);

            // Chiudi il pop-up
            document.querySelector("#chiudi-popup").addEventListener("click", () => {
                popup.remove();
            });

            // Gestisci il submit del form di modifica
            document.querySelector("#modifica-form").addEventListener("submit", (e) => {
                e.preventDefault();

                const datiModifica = {
                    persone: document.querySelector("#persone").value,
                    data: document.querySelector("#data").value,
                    turno: document.querySelector("#turno").value
                };

                fetch(`/script_modifica/${id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(datiModifica),
                })
                .then((response) => {
                    if (response.ok) {
                        alert("Prenotazione modificata con successo!");
                        popup.remove();
                        location.reload(); // Aggiorna la lista delle prenotazioni
                        button.disabled = false
                    } else {
                        return response.json().then((data) => {
                            alert(data.error || "Errore durante la modifica della prenotazione.");
                        });
                    }
                })
                .catch((error) => {
                    console.error("Errore durante la modifica:", error);
                    alert("Si è verificato un errore durante la modifica.");
                });
            });
        });
    });
}
