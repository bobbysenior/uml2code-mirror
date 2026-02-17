#ifndef BANKACCOUNT_H
#define BANKACCOUNT_H

#include <string>
#include <vector>


class BankAccount {
private:
    double balance;

public:
    void deposit();
    void withdraw();

};

#endif // BANKACCOUNT_H