async function fetchTransactions() {
    const response = await fetch('/api/transactions');
    return response.json();
}

async function fetchSummary() {
    const response = await fetch('/api/summary');
    return response.json();
}

async function addTransaction(transaction) {
    const response = await fetch('/api/transactions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(transaction)
    });
    return response.json();
}

async function deleteTransaction(id) {
    const response = await fetch(`/api/transactions/${id}`, {
        method: 'DELETE'
    });
    return response.json();
}

function renderTransactions(transactions) {
    const container = document.getElementById('transactions-container');
    container.innerHTML = transactions.map(trans => `
        <div class="transaction-item">
            <div class="transaction-info">
                <span class="transaction-amount ${trans.type === '收入' ? 'income' : 'expense'}">
                    ${trans.type === '收入' ? '+' : '-'}¥${trans.amount.toFixed(2)}
                </span>
                <span class="transaction-category">${trans.category}</span>
            </div>
            <div class="transaction-details">
                ${trans.description || '无描述'} - ${new Date(trans.date).toLocaleDateString('zh-CN')}
            </div>
            <button class="delete-btn" onclick="deleteTransactionHandler(${trans.id})">删除</button>
        </div>
    `).join('');
}

function updateSummary(summary) {
    document.getElementById('total-income').textContent = summary.total_income.toFixed(2);
    document.getElementById('total-expense').textContent = summary.total_expense.toFixed(2);
    document.getElementById('balance').textContent = summary.balance.toFixed(2);
}

async function refreshData() {
    try {
        const [transactions, summary] = await Promise.all([
            fetchTransactions(),
            fetchSummary()
        ]);
        renderTransactions(transactions);
        updateSummary(summary);
    } catch (error) {
        console.error('获取数据失败:', error);
    }
}

async function addTransactionHandler(event) {
    event.preventDefault();
    
    const form = event.target;
    const transaction = {
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        description: document.getElementById('description').value,
        date: document.getElementById('date').value,
        type: document.getElementById('type').value
    };
    
    try {
        await addTransaction(transaction);
        form.reset();
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        await refreshData();
    } catch (error) {
        console.error('添加交易失败:', error);
        alert('添加交易失败，请重试');
    }
}

async function deleteTransactionHandler(id) {
    if (confirm('确定要删除这条交易记录吗？')) {
        try {
            await deleteTransaction(id);
            await refreshData();
        } catch (error) {
            console.error('删除交易失败:', error);
            alert('删除交易失败，请重试');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-transaction-form').addEventListener('submit', addTransactionHandler);
    document.getElementById('date').value = new Date().toISOString().split('T')[0];
    refreshData();
    
    setInterval(refreshData, 30000);
});