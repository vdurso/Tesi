document.addEventListener('DOMContentLoaded', function () {
    const tabLinks = document.querySelectorAll('.tab-link');
    const menuPanels = document.querySelectorAll('.menu-panel');

    tabLinks.forEach(link => {
        link.addEventListener('click', function () {
            console.log("premuto")
            // Rimuove la classe "active" da tutti i bottoni
            tabLinks.forEach(btn => btn.classList.remove('active'));
            // Aggiunge la classe "active" al bottone selezionato
            this.classList.add('active');

            // Nasconde tutti i pannelli del menu
            menuPanels.forEach(panel => panel.classList.remove('active'));
            // Mostra il pannello associato al bottone cliccato
            const menuId = this.getAttribute('data-menu');
            document.getElementById(menuId).classList.add('active');
        });
    });
});
