# API: Commerce, Finance, Company, Database

Source: <https://fakerjs.dev/api/{commerce,finance,company,database}.html>
Method lists are the complete published API (v10 index).

## commerce

department, isbn, price, product, productAdjective, productDescription,
productMaterial, productName, upc

- `productName()` = adjective + material + product composite.

## finance

accountName, accountNumber, amount, bic, bitcoinAddress, creditCardCVV,
creditCardIssuer, creditCardNumber, currency, currencyCode, currencyName,
currencyNumericCode, currencySymbol, ethereumAddress, iban, litecoinAddress,
pin, routingNumber, transactionDescription, transactionType

- Credit card numbers are Luhn-valid but fake; CVV/pin same. Never claim
  they're real payment data.
- `finance.maskedNumber` was REMOVED in v10 with no replacement (PR #3201).

## company

buzzAdjective, buzzNoun, buzzPhrase, buzzVerb, catchPhrase,
catchPhraseAdjective, catchPhraseDescriptor, catchPhraseNoun, name

## database

collation, column, engine, mongodbObjectId, type
