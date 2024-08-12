document.getElementById('add-investment-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const data = {
        coin_name: document.getElementById('coin_name').value,
        buy_price: document.getElementById('buy_price').value,
        amount: document.getElementById('amount').value
    };

    fetch('/investments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('add-investment-result').innerText = data.message;
            loadInvestments();  // Refresh investments list after adding
        })
        .catch(error => console.error('Error:', error));
});

document.getElementById('get-advice-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const data = {
        coin_name: document.getElementById('advice_coin_name').value,
        buy_price: document.getElementById('advice_buy_price').value,
        amount: document.getElementById('advice_amount').value
    };

    fetch('/advice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            // Display user data
            document.getElementById('user-coin-name').innerText = data.user_data.coin_name;
            document.getElementById('user-buy-price').innerText = data.user_data.buy_price;
            document.getElementById('user-amount').innerText = data.user_data.amount;
            document.getElementById('user-current-price').innerText = data.user_data.current_price;
            document.getElementById('user-profit-loss').innerText = `${data.user_data.profit_loss.type} of ${data.user_data.profit_loss.amount}`;

            // Display advice
            document.getElementById('advice-text').innerText = data.advice;
        })
        .catch(error => console.error('Error:', error));
});


document.getElementById('view-investments').addEventListener('click', loadInvestments);

function loadInvestments() {
    fetch('/investments', {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            const investmentsList = document.getElementById('investments-list');
            investmentsList.innerHTML = '';  // Clear the list before reloading

            data.forEach(investment => {
                const investmentItem = document.createElement('div');
                investmentItem.innerHTML = `
                    <p>
                        ID: ${investment.id}, Coin: ${investment.coin_name}, Buy Price: ${investment.buy_price}, 
                        Amount: ${investment.amount}, Current Price: ${investment.current_price}, Profit/Loss: ${investment.profit_loss}
                        <button onclick="editInvestment(${investment.id}, '${investment.coin_name}', '${investment.buy_price}', '${investment.amount}')">Edit</button>
                        <button onclick="deleteInvestment(${investment.id})">Delete</button>
                    </p>
                `;
                investmentsList.appendChild(investmentItem);
            });
        })
        .catch(error => console.error('Error:', error));
}

function editInvestment(id, coin_name, buy_price, amount) {
    const newCoinName = prompt("Enter new Coin Name:", coin_name);
    const newBuyPrice = prompt("Enter new Buy Price:", buy_price);
    const newAmount = prompt("Enter new Amount:", amount);

    if (newCoinName && newBuyPrice && newAmount) {
        const data = {
            coin_name: newCoinName,
            buy_price: newBuyPrice,
            amount: newAmount
        };

        fetch(`/investments/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadInvestments();  // Refresh investments list after updating
            })
            .catch(error => console.error('Error:', error));
    }
}

function deleteInvestment(id) {
    if (confirm("Are you sure you want to delete this investment?")) {
        fetch(`/investments/${id}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadInvestments();  // Refresh investments list after deleting
            })
            .catch(error => console.error('Error:', error));
    }
}
