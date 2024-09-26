document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('#request-menu button');
    const responseButtons = document.getElementById('response-buttons');
    const atcMessages = document.getElementById('atc-message-box');

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const action = this.id;
            fetch(`/request/${action}`)
                .then(response => response.json())
                .then(data => {
                    atcMessages.innerHTML = `<p>ATC: ${data.message}</p>`;
                    if (data.showResponseButtons) {
                        responseButtons.style.display = 'block';
                    }
                    
                    // Mark the request as done with a green check in the circle
                    const statusCircle = document.getElementById(`${action}-status`);
                    if (statusCircle) {
                        statusCircle.classList.add('visible');
                        statusCircle.innerHTML = '✔';
                    }
                });
        });
    });

    document.querySelectorAll('#response-buttons button').forEach(button => {
        button.addEventListener('click', function () {
            const action = this.id;
            fetch(`/response/${action}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Checkmark action when response is received
                        const statusCircle = document.getElementById(`${data.request}-status`);
                        if (statusCircle) {
                            statusCircle.classList.add('visible');
                            statusCircle.innerHTML = '✔';
                        }
                    }
                });
        });
    });
});
