class BankAccount {
public:
    CreditCard relation0;
    Customer linked_customer_1;
    Customer linked_customer_2;
    void deposit();
    void withdraw();
private:
    double balance;
};