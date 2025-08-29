// JavaScript source code
fetch('http://127.0.0.1:5000/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: "Привет!" })  // Должен быть объект с ключом "message"
})
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Ответ:', data);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });