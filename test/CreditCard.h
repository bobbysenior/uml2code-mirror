#ifndef CREDITCARD_H
#define CREDITCARD_H

#include <string>
#include <vector>

class CreditCard : public Wallet, public IPaymentProcessor {
public:
    void charge();

private:
    std::string cardNumber;

};

#endif // CREDITCARD_H