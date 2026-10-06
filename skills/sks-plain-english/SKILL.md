---
name: sks-plain-english
description:
  "Use when writing or revising technical English — docs, runbooks, commits,
  PR and issue bodies, error messages — under ASD-STE100 Simplified Technical
  English rules."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - writing
      - documentation
      - asd-ste100
    related_skills:
      - sks-github-text-authoring
      - sks-commit
      - sks-pr
      - sks-doc
      - sks-issue
platforms:
  - linux
  - macos
  - windows
---

# Plain English

Write technical English under ASD-STE100 Simplified Technical English. STE
is the controlled language that aerospace and defense manufacturers use for
maintenance documentation: 53 writing rules in 9 sections, built so a tired
non-native reader cannot misread an instruction on the first pass. The same
rules strip the usual signs of AI-generated text: long sentences, synonym
rotation, hedges, filler, decorative clauses.

The official dictionary holds about 900 approved words, each with one
meaning and one part of speech. ASD copyrights it; the standard itself is a
free download at asd-ste100.org. The mechanics below apply without the
dictionary: one word, one meaning, one part of speech.

`sks-github-text-authoring` owns prose mechanics for GitHub text: line
wrapping, `@` escaping, body transport. This skill owns sentence content.
Both apply when drafting a commit, issue, or PR body.

## When to Use

- Write or revise any of: documentation, runbooks, commit messages, PR and
  issue bodies, error messages, agent-facing instructions.
- The user names STE, ASD-STE100, Simplified Technical English, or asks for
  a compliance check.
- Check existing text for STE compliance instead of rewriting it.

Not for marketing copy, blog voice, or brand writing: STE deletes
persuasion by design. Say so and offer it for the docs instead.

Two modes:

| Mode | When | What you apply |
| ---- | ---- | -------------- |
| Pragmatic, the default | Clear text is the goal | All structural rules; domain vocabulary stays |
| Strict | The user names STE or compliance | Structural rules plus full vocabulary discipline |

In strict mode, state that full compliance needs the official dictionary.

## Procedure

1. **Classify each passage.** Procedural text tells the reader what to do.
   Descriptive text explains what a thing is or does. Every rule below
   depends on the class. Do not mix the two in one passage.

   | | Procedural | Descriptive |
   | --- | --- | --- |
   | Verb form | Imperative | Simple present, past, future |
   | Sentence limit | 20 words | 25 words |
   | Unit rule | One instruction per sentence | One topic per paragraph |

2. **Fix the vocabulary before drafting.** One concept, one word, through
   the whole document.

   - One name per item. Do not call it config here and settings there.
   - One check verb. The dictionary rejects check, verify, confirm, and
     ensure as verbs. Strict mode uses `make sure that`.
   - Modal ladder: a requirement is must. may, might, and could for
     possibility become can. would becomes an if sentence. A bare should
     is deleted or restated as fact. Models read should as optional.
   - One verb per action: compress the file, not perform compression of
     the file. No phrasal verbs: set up becomes install or configure.
   - Domain nouns and verbs are legal technical words: webhook, commit,
     deploy, merge. Do not verb a noun or noun a verb: send the event to
     the webhook, never webhook the event.
   - American spelling.

3. **Apply the structural rules.**

   - Sentences are short. One instruction per sentence. Keep articles and
     the conjunction that. No contractions: complete grammar, not
     telegraph style.
   - A condition goes before its command, divided by a comma: If the
     build fails, read the log.
   - Permitted verb forms: infinitive, imperative, simple present, simple
     past, simple future, past participle as adjective. No present
     perfect or past perfect: the migration is complete, never has
     completed. An -ing form is legal only inside a technical noun.
   - Active voice for procedures. Passive is legal in descriptive text
     only when the actor is unknown.
   - A noun cluster is at most three words. Break longer chains with of,
     on, in, or for.
   - No semicolons. Write two sentences.
   - One topic per paragraph, at most six sentences. Use a vertical list
     for sequences, conditions, and enumerations.
   - Warnings lead: risk-level word first, then the command, then the
     risk. CAUTION: Do not use the `--force` flag against production.
     The flag deletes rows that do not match the source.

4. **Leave the untouchables exact**, even when they break vocabulary
   rules: code, inline code, identifiers, commands, flags, file paths,
   quoted errors and log lines, product names, config keys. In word
   counts, quoted text, numbers with units, identifiers, and hyphenated
   words each count as one word, so a long flag does not blow the
   sentence budget.

5. **Run the self-check before delivery.**

   - Count words in the longest sentences. Split anything over the
     class limit.
   - Search for contractions, has been, have been, should, semicolons,
     and -ing verbs after a comma.
   - Search for every if and when. Each opens its sentence, before the
     command.
   - Search for the check verbs you did not pick in step 2.

Each step is done when its artifact sits in the draft: the classification
marked, the vocabulary fixed, the rules applied, the untouchables verified,
the self-check findings fixed.

## Pitfalls

- **Citing rule numbers from memory.** The numbering is unintuitive and
  models invent it. Report a violation as the offending text plus a
  compliant rewrite, or cite only numbers this body states.
- **Synonym rotation.** A second word for the same concept reads as
  richness and costs the reader a mapping. One concept, one word.
- **Telegraph style.** Dropping articles to shorten a sentence creates
  ambiguity; the standard rejects it explicitly. Short sentences, full
  grammar.
- **Burying the instruction.** An instruction after two explanation
  clauses is a misread waiting to happen. Condition first, then the
  command.
- **Treating the dictionary as required.** The mechanics apply without
  it. Only a strict compliance claim needs the official download.

## Verification

- Every procedure sentence is imperative, at most 20 words, and leads
  conditions first.
- No semicolons, no contractions, no present perfect in the final text.
- One word per concept across the whole document.
- Code, commands, and quoted errors are byte-identical to the source.

## See also

- `sks-github-text-authoring` — prose mechanics for GitHub text.
- `sks-commit`, `sks-pr`, `sks-issue` — the surfaces this style feeds.
- `sks-doc` — docs-directory workflow that carries the final text.
