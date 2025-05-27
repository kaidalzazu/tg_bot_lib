// Можно оставить пустым или добавить свою логику
function searchBooks() {
    const input = document.getElementById('searchInput').value;
    fetch(`/search?q=${input}`)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('bookList');
            list.innerHTML = "";
            data.forEach(book => {
                const li = document.createElement("li");
                li.textContent = `${book.title} — ${book.author} (ID: ${book.id})`;
                list.appendChild(li);
            });
        });
}