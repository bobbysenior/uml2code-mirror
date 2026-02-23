class Wallet {
public:
    virtual ~Wallet() = default;
    void addMoney();
private:
    double amount;
};