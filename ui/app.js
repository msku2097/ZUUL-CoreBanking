const API_URL = "http://localhost:8000/graphql";

// Function to show notifications
function showNotification(message, type) {
    const notification = document.getElementById("notification");
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = "block";
    setTimeout(() => {
        notification.style.display = "none";
    }, 3000);
}

// Function to create a new user
async function createUser(event) {
    event.preventDefault();
    const accountId = document.getElementById("accountId").value;
    const customerName = document.getElementById("customerName").value;
    const initialBalance = parseFloat(document.getElementById("initialBalance").value);

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    createUser(account_id: "${accountId}", customer_name: "${customerName}", funds: ${initialBalance}, interest_rate: 1.5) {
                        account_id
                        customer_name
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.createUser) {
        showNotification("User created successfully!", "success");
    } else {
        showNotification("Error creating user", "error");
    }
}

// Function to update funds
async function updateFunds(event) {
    event.preventDefault();
    const accountId = document.getElementById("updateAccountId").value;
    const amount = parseFloat(document.getElementById("amount").value);

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    updateFunds(account_id: "${accountId}", amount: ${amount})
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.updateFunds) {
        showNotification(result.data.updateFunds, "success");
    } else {
        showNotification("Error updating funds", "error");
    }
}

// Function to transfer funds between accounts
async function transferFunds(event) {
    event.preventDefault();
    const fromAccountId = document.getElementById("fromAccountId").value;
    const toAccountId = document.getElementById("toAccountId").value;
    const amount = parseFloat(document.getElementById("transferAmount").value);

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    transfer(from_account_id: "${fromAccountId}", to_account_id: "${toAccountId}", amount: ${amount})
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.transfer) {
        showNotification("Transfer completed successfully!", "success");
    } else {
        showNotification("Error transferring funds", "error");
    }
}

// Function to view user profile, including loan details
async function viewUserProfile(event) {
    event.preventDefault();
    const accountId = document.getElementById("profileAccountId").value;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                query {
                    user(account_id: "${accountId}") {
                        account_id
                        customer_name
                        funds
                        loans {
                            amount
                            interest_rate
                            installments
                            remaining_balance
                        }
                        interest_rate
                        action_history
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.user) {
        const user = result.data.user;
        document.getElementById("profileDetails").innerHTML = `
            <p><strong>Account ID:</strong> ${user.account_id}</p>
            <p><strong>Customer Name:</strong> ${user.customer_name}</p>
            <p><strong>Funds:</strong> $${user.funds}</p>
            <p><strong>Interest Rate:</strong> ${user.interest_rate}%</p>
            <h5>Loans:</h5>
            <ul>
                ${user.loans.map(loan => `
                    <li>Amount: $${loan.amount}, Interest Rate: ${loan.interest_rate}%, 
                    Installments: ${loan.installments}, Remaining Balance: $${loan.remaining_balance}</li>
                `).join('')}
            </ul>
            <h5>Action History:</h5>
            <ul>${user.action_history.map(action => `<li>${action}</li>`).join('')}</ul>
        `;
        showNotification("User profile loaded", "success");
    } else {
        showNotification("User not found", "error");
    }
}

// Function to create a new loan
async function createLoan(event) {
    event.preventDefault();
    const accountId = document.getElementById("loanAccountId").value;
    const amount = parseFloat(document.getElementById("loanAmount").value);
    const interestRate = parseFloat(document.getElementById("loanInterestRate").value);
    const installments = parseInt(document.getElementById("loanInstallments").value);

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    createLoan(account_id: "${accountId}", amount: ${amount}, interest_rate: ${interestRate}, installments: ${installments}) {
                        success
                        message
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.createLoan.success) {
        showNotification(result.data.createLoan.message, "success");
    } else {
        showNotification(result.data.createLoan.message || "Error creating loan", "error");
    }
}

// Function to update an existing loan
async function updateLoan(event) {
    event.preventDefault();
    const accountId = document.getElementById("updateLoanAccountId").value;
    const newAmount = parseFloat(document.getElementById("updateLoanAmount").value);
    const newInterestRate = parseFloat(document.getElementById("updateLoanInterestRate").value);
    const newInstallments = parseInt(document.getElementById("updateLoanInstallments").value);

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    modifyLoan(account_id: "${accountId}", new_amount: ${newAmount}, new_interest_rate: ${newInterestRate}, new_installments: ${newInstallments}) {
                        success
                        message
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.modifyLoan.success) {
        showNotification(result.data.modifyLoan.message, "success");
    } else {
        showNotification(result.data.modifyLoan.message || "Error modifying loan", "error");
    }
}

// Function to delete a loan
async function deleteLoan(event) {
    event.preventDefault();
    const accountId = document.getElementById("deleteLoanAccountId").value;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    deleteLoan(account_id: "${accountId}") {
                        success
                        message
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.deleteLoan.success) {
        showNotification(result.data.deleteLoan.message, "success");
    } else {
        showNotification(result.data.deleteLoan.message || "Error deleting loan", "error");
    }
}

// Function to delete a user
async function deleteUser(event) {
    event.preventDefault();
    const accountId = document.getElementById("deleteUserAccountId").value;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `
                mutation {
                    deleteUser(account_id: "${accountId}") {
                        success
                        message
                    }
                }
            `
        })
    });

    const result = await response.json();
    if (result.data && result.data.deleteUser.success) {
        showNotification(result.data.deleteUser.message, "success");
    } else {
        showNotification(result.data.deleteUser.message || "Error deleting user", "error");
    }
}
