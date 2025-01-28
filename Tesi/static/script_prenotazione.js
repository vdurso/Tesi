$(document).ready(function() {
    $('#reservation-form').submit(function(e) {
        e.preventDefault();  
        
        const turno = document.getElementById('turno').value;
        console.log("Turno selezionato:", turno);

        //prepara i dati per inviarli al server
        var datiForm = {
            persone: $('#persone').val(),
            data: $('#data').val(),
            turno: turno
        };
        

        //invio dei dati al server
        $.ajax({
            url: '/prenota',  
            type: 'POST',
            contentType:'application/json',
            data: JSON.stringify(datiForm),  
            success: function(response) {
                alert(response.message);  
                $('#reservation-form')[0].reset();  
            },
            error: function(xhr, status, error) {
                console.log(xhr.responseJSON)
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.error : "Errore nell'invio della prenotazione. Riprova.";
                alert(errorMessage);  
            }
        });
    });
});
