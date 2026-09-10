# API: Person, Internet, Location, Phone

Source: <https://fakerjs.dev/api/{person,internet,location,phone}.html>
Method lists are the complete published API (v10 index).

## person

bio, firstName, fullName, gender, jobArea, jobDescriptor, jobTitle, jobType,
lastName, middleName, prefix, sex, sexType, suffix, zodiacSign

- `person.firstName(sex)` accepts a sex to keep fields consistent; build
  dependent fields in order (see usage.md factory pattern).
- `sexType()` returns `'female' | 'male'`; `gender()` returns text.

## internet

displayName, domainName, domainSuffix, domainWord, email, emoji, exampleEmail,
httpMethod, httpStatusCode, ip, ipv4, ipv6, jwt, jwtAlgorithm, mac, password,
port, protocol, url, userAgent, username

- `internet.email({ firstName, lastName })` accepts names for coherent
  addresses.
- `exampleEmail()` = example.com/example.org domains — safe for demos, won't
  reach real inboxes.
- `username` (lowercase n) since v9; `userName` removed in v10.

## location

buildingNumber, cardinalDirection, city, continent, country, countryCode,
county, direction, language, latitude, longitude, nearbyGPSCoordinate,
ordinalDirection, postalAddress, secondaryAddress, state, street,
streetAddress, timeZone, zipCode

- Replaced the old `address` module (removed v10).
- `nearbyGPSCoordinate` anchors around a point; zipCode may throw
  not-applicable in locales without postal codes (e.g. en_HK) — see
  localization.md.

## phone

imei, number
