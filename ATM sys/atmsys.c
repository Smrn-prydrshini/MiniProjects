/* ATM SYSTEM CODE
   Creating a c program to display the ATM transactions.
   In this program we are taking input from user in terms of the the account no,
   the transaction type, etc.
*/

#include <stdio.h>
#include <stdlib.h>


// Sample account structure

struct Account {
    int accountNumber;
    int pin;
    double balance;
};

int currentAccount = -1; // Current logged-in account index

// declaring a function to display the menu

void displayMenu() 
{
   printf("\nOptions:\n");
    printf("1. Check Balance\n");
    printf("2. Deposit Money\n");
    printf("3. Withdraw Money\n");
    printf("4. Logout\n");
    printf("5. Exit\n");

}

// declaring a function to check and display the balance

void checkBalance(struct Account account) {
    printf("Your balance: $%.2lf\n", account.balance);
}

// declaring a function to deposit money 

void deposit(struct Account *account) {
       double amount;
    printf("Enter the amount to deposit: $");
    scanf("%lf", &amount);
    if (amount > 0) {
        account[currentAccount].balance += amount;
        printf("Deposited $%.2lf. New balance: $%.2lf\n", amount, account[currentAccount].balance);
    } else {
        printf("Invalid deposit amount.\n");
}
}

// declaring a function to withdraw money

void withdraw(struct Account *account) {
    double amount;
    printf("Enter the amount to withdraw: $");
    scanf("%lf", &amount);
    if (amount > 0 && amount <= account[currentAccount].balance) {
        account[currentAccount].balance -= amount;
        printf("Withdrew $%.2lf. New balance: $%.2lf\n", amount, account[currentAccount].balance);
    } else {
        printf("Invalid withdrawal amount or insufficient balance.\n");
    }

}

int main() 
 {

    int choice;

    FILE *file = fopen("accounts.txt", "r"); // Opening file for reading account details
    if (file == NULL) {
        printf("Error opening file for reading.\n");
        return 1;
    }

    struct Account accounts[500]; // Assuming a maximum of 500 accounts
    int numAccounts = 0;

    while (fscanf(file, "%d %d %lf", &accounts[numAccounts].accountNumber, &accounts[numAccounts].pin, &accounts[numAccounts].balance) != EOF) {
        numAccounts++;
    }

    fclose(file);

// using while loop for proper functioning 

    while (1) {
        printf("\nWelcome to the ATM system!\n");
        if (currentAccount == -1) {
            int accountNumber, pin;
            printf("Enter your account number: ");
            scanf("%d", &accountNumber);
            printf("Enter your PIN: ");
            scanf("%d", &pin);

// Authentication process 
            for (int i = 0; i < numAccounts; i++) 
{
                if (accounts[i].accountNumber == accountNumber && accounts[i].pin == pin) {
                    currentAccount = i;
                    break;
                }
            }

            if (currentAccount == -1) {
                printf("Authentication failed. Please try again.\n");
                continue;
            }
        }

        displayMenu(); // calling the displayMenu function

        printf("Enter option: "); 
        scanf("%d", &choice); // taking input for transaction

        switch (choice) {
            case 1:
                checkBalance(accounts[currentAccount]);
                break;
            case 2:
                deposit(&accounts[currentAccount]);
                break;
            case 3:
                withdraw(&accounts[currentAccount]);
                break;
            case 4:
                currentAccount = -1;
                printf("Logged out.\n");
                break;
            case 5:
                file = fopen("accounts.txt", "w"); // Opening file for writing account details
                if (file == NULL) {
                    printf("Error opening file for writing.\n");
                    return 1;
                }

                for (int i = 0; i < numAccounts; i++) {
                    fprintf(file, "%d %d %.2lf\n", accounts[i].accountNumber, accounts[i].pin, accounts[i].balance);
                }

                fclose(file);
                printf("Thank you for using this ATM. Goodbye!\n");
                exit(0);
            default:
                printf("Invalid choice. Please select a valid option.\n");
        }
    }

    return 0;
}



