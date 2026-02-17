#ifndef IPAYMENTPROCESSOR_H
#define IPAYMENTPROCESSOR_H

#include <string>
#include <vector>

class IPaymentProcessor {
public:
    virtual void processPayment() = 0;

};

#endif // IPAYMENTPROCESSOR_H