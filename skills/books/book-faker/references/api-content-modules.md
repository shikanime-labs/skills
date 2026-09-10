# API: Content & Topic Modules

Source: <https://fakerjs.dev/api/{airline,animal,book,color,food,git,hacker>,
image,lorem,music,science,system,vehicle}.html
Method lists are the complete published API (v10 index).

## airline

aircraftType, airline, airplane, airport, flightNumber, recordLocator, seat

## animal

bear, bird, cat, cetacean, cow, crocodilia, dog, fish, horse, insect, lion,
petName, rabbit, rodent, snake, type

- `animal.type` pool is tiny (44) — collides fast (see unique-data.md).

## book

author, format, genre, publisher, series, title

## color

cmyk, colorByCSSColorSpace, cssSupportedFunction, cssSupportedSpace, hsl,
human, hwb, lab, lch, rgb, space

- `color.rgb()` replaced `internet.color` (removed v10).

## food

adjective, description, dish, ethnicCategory, fruit, ingredient, meat, spice,
vegetable

## git

branch, commitDate, commitEntry, commitMessage, commitSha

- `commitEntry` embeds a relative date → fix refDate for reproducibility.

## hacker

abbreviation, adjective, ingverb, noun, phrase, verb

## image

avatar, avatarGitHub, dataUri, personPortrait, url, urlLoremFlickr,
urlPicsumPhotos

- URLs point at THIRD-PARTY services (picsum, loremflickr, GitHub avatars);
  tests depending on them can flake on network. `dataUri` is offline-safe.

## lorem

lines, paragraph, paragraphs, sentence, sentences, slug, text, word, words

- v10 word-length constraint: `{ strategy: 'any-length' }` restores v9
  leniency (see upgrading.md).

## music

album, artist, genre, songName

## science

chemicalElement, unit

## system

commonFileExt, commonFileName, commonFileType, cron, directoryPath, fileExt,
fileName, filePath, fileType, mimeType, networkInterface, semver

## vehicle

bicycle, color, fuel, manufacturer, model, type, vehicle, vin, vrm
