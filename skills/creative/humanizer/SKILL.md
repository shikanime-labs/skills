---
name: humanizer
description: "Use when humanizing or de-slopping text: strip AI-isms, add real voice, or match a user's voice sample."
version: 2.5.1
author: Siqi Chen (@blader, https://github.com/blader/humanizer), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, editing, humanize, anti-ai-slop, voice, prose, text]
    category: creative
    homepage: https://github.com/blader/humanizer
    related_skills: [songwriting-and-ai-music]
---

# Humanizer: Remove AI Writing Patterns

Identify and remove signs of AI-generated text. Based on Wikipedia's "Signs of
AI writing" guide (WikiProject AI Cleanup). LLMs guess the statistically most
likely completion, which is how these tells get baked in.

## When to load

- User asks to "humanize", "de-AI", "de-slop", or "un-ChatGPT" text
- Rewrite a draft (blog, essay, PR description, docs, memo, email, resume
  bullet) so it does not read as LLM output
- Match the user's voice in writing you produce
- Review text for AI tells before publishing
- Your own user-facing prose (release notes, PR descriptions, summaries)

## Workflow

1. Inline text: work in place, reply with the rewrite.
2. File: `read_file` to load; apply with targeted `patch` per section or
   `write_file` for a full rewrite; show a diff or the changed section, never
   silently overwrite.
3. Voice sample: read it first (Voice Calibration below), then rewrite.

Core loop: identify patterns, rewrite them, present a draft, ask yourself
"What makes the below so obviously AI generated?", answer with the remaining
tells, revise, present the final version. The self-audit pass is mandatory.
Deliver: draft rewrite, the audit bullets, final rewrite.

## Voice Calibration (when the user supplies a sample)

Read the sample and note: sentence-length rhythm, word-choice register,
paragraph openings, punctuation habits (dashes, parentheticals, semicolons),
recurring tics, transition style. Swap the sample's patterns in: if they
write short sentences, do not produce long ones; if they say "stuff" and
"things", do not upgrade to "elements" and "components". No sample: use the
default voice below.

## Personality and soul

Clean but voiceless is still a tell. Signs of soulless writing: uniform
sentence length and structure, no opinions, no uncertainty, no first person,
no humor or edge, reads like a press release.

- Have opinions: report the facts, then react to them.
- Vary rhythm: short punchy sentences next to longer ones.
- Acknowledge mixed feelings: "impressive but also unsettling" beats
  "impressive".
- Use "I" where it fits; be specific about feelings instead of "concerning".
- Let some mess in: tangents and asides are human.

"The experiment produced interesting results" → "I genuinely don't know how
to feel about this one. 3 million lines of code, generated while the humans
presumably slept."

## The 34 patterns

Each entry: detection cues, then a before → after pair.

### Content patterns

**1. Inflated significance/legacy.** Watch: stands/serves as, is a
testament/reminder, vital/significant/crucial/pivotal/key role, underscores
its importance, reflects broader, enduring/lasting, setting the stage for,
key turning point, evolving landscape, indelible mark, deeply rooted.
"established in 1989, marking a pivotal moment in the evolution of regional
statistics" → "was established in 1989 to collect and publish regional
statistics independently from Spain's national office."

**2. Inflated notability.** Watch: independent coverage, local/regional/
national media outlets, written by a leading expert, active social media
presence. Cite one specific source instead of listing outlets.
"cited in the NYT, BBC, FT, and The Hindu; maintains an active social media
presence" → "In a 2024 New York Times interview, she argued that AI
regulation should focus on outcomes rather than methods."

**3. Superficial -ing analyses.** Watch: highlighting/underscoring/
emphasizing..., ensuring..., reflecting/symbolizing..., contributing to...,
cultivating/fostering..., encompassing..., showcasing...
"a palette that resonates with the region's natural beauty, symbolizing
bluebonnets, reflecting the community's deep connection" → "The temple uses
blue, green, and gold. The architect said these were chosen to reference
local bluebonnets and the Gulf coast."

**4. Promotional language.** Watch: boasts a, vibrant, rich (figurative),
profound, enhancing its, exemplifies, commitment to, natural beauty,
nestled, in the heart of, breathtaking, must-visit, stunning, renowned,
groundbreaking (figurative).
"Nestled within the breathtaking region of Gonder... a vibrant town with a
rich cultural heritage and stunning natural beauty" → "a town in the Gonder
region of Ethiopia, known for its weekly market and 18th-century church."

**5. Vague attribution / weasel words.** Watch: industry reports, observers
have cited, experts argue, some critics argue, several sources/publications.
Attribute to a specific source or drop the claim.
"Experts believe it plays a crucial role in the regional ecosystem" →
"supports several endemic fish species, according to a 2019 survey by the
Chinese Academy of Sciences."

**6. Formulaic "challenges" sections.** Watch: Despite its..., faces several
challenges, Despite these challenges, Challenges and Legacy, Future Outlook.
Replace with concrete facts.
"Despite these challenges... continues to thrive as an integral part of
Chennai's growth" → "Traffic congestion increased after 2015 when three IT
parks opened. The municipal corporation began a stormwater project in 2022."

### Language and grammar

**7. AI vocabulary.** Watch: actually, additionally, align with, crucial,
delve, emphasizing, enduring, enhance, fostering, garner, highlight,
interplay, intricate/intricacies, key (adj), landscape (abstract), pivotal,
showcase, tapestry (abstract), testament, underscore, valuable, vibrant.
Marketing clichés, same tell: at the end of the day, when it comes to, in a
world where, moving forward, circle back, deep dive, game-changer, double
down, take a step back, on the same page, make no mistake, it turns out, let
me be clear, navigate (for challenges), lean into, unpack (before analysis),
straightforward (to describe anything).

**8. Copula avoidance.** serves as / stands as / marks / represents; boasts /
features / offers. Use is/are/has.
"serves as LAAA's exhibition space... boasts over 3,000 square feet" → "is
LAAA's exhibition space... has four rooms totaling 3,000 square feet."

**9. Negative parallelism and tailing negation.** "Not only...but", "It's
not just X, it's Y", plus clipped tails ("no guessing", "no wasted motion")
tacked onto sentence ends instead of real clauses.
"It's not merely a song, it's a statement" → "The heavy beat adds to the
aggressive tone." / "The options come from the selected item, no guessing" →
"The options come from the selected item without forcing the user to guess."

**10. Rule of three.** Forced triads ("innovation, inspiration, and industry
insights") compress to the one or two real items.

**11. Elegant variation.** Synonym cycling (protagonist / main character /
central figure / hero). Pick one term and repeat it.

**12. False ranges.** "from X to Y" where X and Y share no scale.
"from the singularity of the Big Bang to the grand cosmic web, from the
birth and death of stars to the enigmatic dance of dark matter" → "The book
covers the Big Bang, star formation, and current theories about dark
matter."

**13. Passive voice and subjectless fragments.** Rewrite when active voice
is clearer.
"No configuration file needed. The results are preserved automatically." →
"You do not need a configuration file. The system preserves the results
automatically."

### Style

**14. Em dash overuse.** Most em dashes rewrite cleaner with commas,
periods, or parentheses.
"promoted by Dutch institutions—not by the people... continues—even in
official documents" → "promoted by Dutch institutions, not by the people...
continues in official documents."

**15. Mechanical boldface.** Bold a term at first use only, or not at all.
"**OKRs (Objectives and Key Results)**, **KPIs**, the **Business Model
Canvas (BMC)**" → "OKRs, KPIs, and visual strategy tools like the Business
Model Canvas."

**16. Inline-header vertical lists.** "**User Experience:** ...,
**Performance:** ..., **Security:** ..." → one flowing sentence covering the
real deltas.

**17. Title case in headings.** "Strategic Negotiations And Global
Partnerships" → "Strategic negotiations and global partnerships."

**18. Emojis as decoration.** 🚀/💡/✅ on headings and bullets → plain
sentences.

**19. Curly quotation marks.** Replace with straight quotes.

### Communication artifacts

**20. Chat artifacts pasted as content.** I hope this helps, Of course!,
Certainly!, You're absolutely right!, Would you like..., let me know, here
is a...
"Here is an overview... I hope this helps! Let me know if you'd like me to
expand" → delete the wrapper, keep the content.

**21. Knowledge-cutoff disclaimers.** as of [date], up to my last training
update, while specific details are limited/scarce, based on available
information. State the fact and its source, or omit.
"While specific details are not extensively documented in readily available
sources" → "The company was founded in 1994, according to its registration
documents."

**22. Sycophancy.** "Great question!... That's an excellent point" →
address the point directly.

### Filler and hedging

**23. Filler phrases.** "in order to" → "to"; "due to the fact that" →
"because"; "at this point in time" → "now"; "in the event that" → "if"; "has
the ability to process" → "can process"; "it is important to note that the
data shows" → "the data shows".

**24. Excessive hedging.** "It could potentially possibly be argued that the
policy might have some effect" → "The policy may affect outcomes."

**25. Generic positive conclusions.** "The future looks bright... exciting
times lie ahead" → the concrete next fact ("plans to open two more locations
next year").

**26. Uniform hyphenated pairs.** third-party, cross-functional,
client-facing, data-driven, decision-making, well-known, high-quality,
real-time, long-term, end-to-end. Humans hyphenate these inconsistently;
less-common or technical compounds are fine to keep.

**27. Persuasive authority tropes.** The real question is, at its core, in
reality, what really matters, fundamentally, the deeper issue, the heart of
the matter. The sentence that follows usually restates an ordinary point;
cut to it.

**28. Signposting.** Let's dive in, let's explore, here's what you need to
know, now let's look at, without further ado. Do the thing instead of
announcing it.

**29. Fragmented headers.** A heading followed by a one-line paragraph that
restates the heading ("## Performance / Speed matters."). Delete the warm-up
line.

### Rhythm and rhetoric

**30. Forced metaphors.** Strained or mixed metaphors, figurative
substitution where a plain word is clearer, or a metaphor explained right
after use. If it does not earn its place, say the literal thing.
"a garden we must tend, pruning dead branches and planting seeds of
innovation so the ecosystem can flourish" → "Delete unused code and add the
features users are asking for."

**31. Punchy kickers and dramatic fragmentation.** Staccato subjectless
fragments ("Pay for what it does. Not promises. It just works."), a short
quotable line ending every section, cutesy appositive fragments ("the
catalog, honestly priced"). Distinct from 13: the tell is showmanship, not a
hidden actor. Fold back into a real sentence with a subject.
"The catalog, honestly priced. Pay for what it does. Not promises." → "The
catalog is priced by usage, so you pay for the calls you actually make
rather than a flat monthly fee."

**32. Rhetorical questions answered immediately.** "What makes an API good?
It comes down to predictability." → "A good API is predictable, so
developers know exactly what they will get back."

**33. Sentence-opener tics.** So..., Look,, habitual sentence-initial
And/But, "I think"/"I believe" when stating a fact, adverb openers
(Interestingly, Importantly, Notably, Crucially, Essentially, Ultimately).
Drop the opener, start with the substance.

**34. Reassurance kickers.** And that's okay, and that's fine, there's
nothing wrong with that, no shame in..., you're not alone, it's completely
normal. The reader did not ask for comfort. Make the point and stop.

## Attribution

Ported from [blader/humanizer](https://github.com/blader/humanizer) (MIT,
preserved in the LICENSE file alongside this SKILL.md), itself based on
[Wikipedia: Signs of AI
writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup). Original author: Siqi Chen (@blader). The original
29 patterns and example pairs come from upstream; patterns 30-34 and the
marketing-cliché list in 7 are Hermes additions. The full worked example
(draft, audit, final) lives upstream; this file keeps one pair per pattern.
