document.addEventListener("DOMContentLoaded", function () {
    const evaluationForm = document.getElementById('evaluationForm');
    const loadingIndicator = document.getElementById('loading');

    if (!evaluationForm || !loadingIndicator) {
        console.error('Form or loading indicator missing');
        return;
    }

    evaluationForm.addEventListener('submit', function (e) {
        e.preventDefault();
        loadingIndicator.style.display = 'block';

        const formData = new FormData();
        formData.append('expected_file', document.getElementById('expected_file').files[0]);
        formData.append('student_file', document.getElementById('student_file').files[0]);

        fetch('/evaluate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            if (data.redirect) {
                window.location.href = data.redirect;  // Redirect to result page
            } else {
                console.error('No redirect URL provided');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
        });
    });
});
