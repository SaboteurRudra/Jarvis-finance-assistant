document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('expense-form');
    const searchInput = document.getElementById('search-input');
    const getAdviceBtn = document.getElementById('get-advice-btn');
    
    // Load initial expenses
    fetchExpenses();

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const amount = document.getElementById('amount').value;
        const category = document.getElementById('category').value;
        const description = document.getElementById('description').value;

        await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, category, description })
        });

        form.reset();
        fetchExpenses();
    });

    // Search Category
    searchInput.addEventListener('input', (e) => {
        fetchExpenses(e.target.value);
    });

    // Get Advice
    getAdviceBtn.addEventListener('click', async () => {
        const adviceContent = document.getElementById('advice-content');
        const adviceText = document.getElementById('advice-text');
        const loader = document.getElementById('advice-loader');
        
        adviceContent.classList.remove('hidden');
        adviceText.classList.add('hidden');
        loader.classList.remove('hidden');
        getAdviceBtn.disabled = true;

        try {
            const res = await fetch('/api/advice');
            const data = await res.json();
            
            // Format basic markdown newlines and bold tags
            let formattedText = data.advice.replace(/\n/g, '<br>');
            formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            adviceText.innerHTML = formattedText;
        } catch (err) {
            adviceText.textContent = "Failed to connect to the AI.";
        }

        loader.classList.add('hidden');
        adviceText.classList.remove('hidden');
        getAdviceBtn.disabled = false;
    });

    // Fetch and render expenses
    async function fetchExpenses(category = '') {
        const res = await fetch(`/api/expenses?category=${encodeURIComponent(category)}`);
        const expenses = await res.json();
        
        const list = document.getElementById('expenses-list');
        list.innerHTML = '';
        
        let total = 0;
        
        if (expenses.length === 0) {
            list.innerHTML = '<li class="expense-item"><span class="text-muted">No expenses found.</span></li>';
        } else {
            expenses.forEach(e => {
                total += e.amount;
                const li = document.createElement('li');
                li.className = 'expense-item';
                li.innerHTML = `
                    <div class="expense-info">
                        <span class="category">${e.category}</span>
                        <span class="desc">${e.description}</span>
                        <span class="date">${e.date}</span>
                    </div>
                    <div class="expense-amount">$${e.amount.toFixed(2)}</div>
                `;
                list.appendChild(li);
            });
        }

        const average = expenses.length > 0 ? (total / expenses.length) : 0;
        
        document.getElementById('total-spent').textContent = `$${total.toFixed(2)}`;
        document.getElementById('average-spent').textContent = `$${average.toFixed(2)}`;
    }
});
