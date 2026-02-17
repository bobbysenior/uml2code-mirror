#ifndef IPAYMENTPROCESSOR_H
#define IPAYMENTPROCESSOR_H

#include <string>

class IPaymentProcessor {
public:
    virtual ~IPaymentProcessor() {}
    virtual void processPayment() = 0;
};
#endif // IPAYMENTPROCESSOR_H