#ifndef BANKACCOUNT_H
#define BANKACCOUNT_H

#include <string>
#include <vector>

class BankAccount {
public:
    void deposit();
    void withdraw();

private:
    double balance;

};

#endif // BANKACCOUNT_H