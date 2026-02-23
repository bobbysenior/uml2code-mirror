class CreditCard : public Wallet, public IPaymentProcessor {
public:
    void charge();
    void pay(customer : Customer, amount : int);
private:
    String cardNumber;
    int coucou;
};