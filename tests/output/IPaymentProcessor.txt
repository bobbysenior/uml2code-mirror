class IPaymentProcessor {
public:
    virtual ~IPaymentProcessor() = default;
    virtual void processPayment() = 0;
};