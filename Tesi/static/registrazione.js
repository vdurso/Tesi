$(document).ready(function() {
    $('#form-registrazione').submit(function(e){
        e.preventDefault();

        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; //regex per validare mail
        var phoneRegex = /^[0-9]{8,15}$/; //regex per validare il numero di telefono

        var datiUtente = {
            nome: $('#nome').val(),
            cognome: $('#cognome').val(),
            email: $('#email').val(),
            telefono: $('#telefono').val(),
            username: $('#username').val(),
            password: $('#password').val()
        };

          //controllo sul campo mail
          if(!emailRegex.test(datiUtente.email)){
            alert("Inserire una mail valida!");
            return;
        }
        
        //controllo sul campo telefono
        if(!phoneRegex.test(datiUtente.telefono)){
            alert("Inserire un numero di telefono valido!")
            return;
        }

        $.ajax({
            url: '/registra',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(datiUtente),
            success: function(response){
                alert(response.message)
                $('#form-registrazione')[0].reset()
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.error : "Errore nell'invio della prenotazione. Riprova.";
                alert(errorMessage);  
            }
        })
    })
})