# FUDG-GFL Abridged Annotation Guidelines 1.3

Chris Dyer
Brendan O’Connor
Nathan Schneider
David Bamman
Noah A. Smith
Michael T. Mordowanec

*Document history:*
2014-03-12: version 1.0: forked from main guidelines


This document is about two related things.

1. An enhanced syntactic annotation scheme built on unlabeled dependencies, which we call **Fragmentary Unlabeled Dependency Grammar (FUDG)**.

2. A lightweight notation for describing annotations over graph fragments, which we call **Graph Fragment Language (GFL)**.

### Indicating dependency edges
In dependency annotation we are concerned with the syntactic relationships between words. The primary relationship is the dependency. A simplistic
way of conceptualizing the dependency is that one word is the dependent of another word if it is modifying it in some way. The arguments of a verb are also
dependents of it, adjectives are dependents of the nouns they modify, similarly with adverbs.
Left and right arrows (marked with `<` or `>`) are used to indicate a dependency, pointing **from** the dependent **to** the head.  For example,

> I saw the cat

could be represented as the list of all the dependency edges,

	saw < I
	saw < cat
	cat < the

It is always possible to completely describe a dependency graph with a long list of pairs, but there are also terser shortcuts.

### Associativity and Precedence in Chains

Arrows can be chained together to form longer chains, and ambiguities resolved with parentheses. The **head** of an expression enclosed in (parentheses) is the only element that becomes a head or dependent.  This is useful to naturally preserve surface orderings.  For example, the *"I saw the cat" *example could have been written as:

	I > saw < (the > cat)

When working out the meanings of chains, keep in mind that right arrows associate to the left, i.e., `a > b > c` is the same as `(a > b) > c`, and left arrows associate to the right, i.e., `a < b < c` is the same as `a < (b < c)`.

The double-headed expression **`a < b > c`** violates the single-parent constraint of our syntactic formalism, and is thus disallowed by the parser.
## Coordination nodes

Coordination represents a particular problem in pure dependency formalisms. We handle them by permitting the introduction of **coordination nodes** using a special ternary operator.

> He and his wife own smash burger

```bash
$a :: {He wife} :: and
wife < his
$a > own < [smash burger]
his = He
```
## Multiwords

It is often advantageous to treat multiple tokens as a single virtual word. This can be done by enclosing the words in [square brackets]. For example:

> **Brendan O’Connor** helped **write up** this guide.

    [Brendan O’Connor] > helped < [write up] < (this > guide)

The formalism makes no commitment to the surface ordering within a square bracket construct. The same graph description would work for:

> Brendan O’Connor helped **write** this guide **up**.

   ![Brendan O’Connor helped write this guide up.](writeup.0.png)

Multiwords allow an annotator to punt on expressions that are best understood as idiosyncratic phrases or that have forbiddingly complicated compositional analyses, while still describing their relationship with the rest of the sentence (e.g. [putnam_catenae_examples](https://github.com/brendano/gfl_syntax/blob/master/anno/putnam_catenae_examples.anno) from Osborne et al 2011).

We generally reserve multiwords for the following cases that are semantically coherent but not easy to analyze syntactically:

  1. multiword proper names: `[Brendan O’Connor]`
  2. verb-particle constructions: `[wake up]`
  3. multiple input tokens conventionally written as one word: `[over priced]`
  4. highly noncompositional compounds and foreign expressions: `[class act]`, `the > [lost and found]`, `[post hoc]`
  5. syntactically difficult idioms: `[let alone]`, `[had better]` (see [quasi-modals](#verb-complexes))

But we try to decompose idioms that have a plausible (if atypical) syntactic analysis:

    kick < (the > bucket)
    I > (kid < you) < not
    be < on < (the > verge < of < victory)



![He and his wife own smash burger](football_wives_small.0.png)

The coordination node binds to the word *"and"*, and its node children are both *“He”* and *“wife”*.  This is described with the double-colon `::`  ternary operator. `$a` is the name of the node in the GFL.  It must begin with a dollar sign (`$`).

If there are multiple coordinator words, they should all be listed, except for punctuation.

> ice cream and~1 cake and~2 asparagus

```bash
$x :: {[ice cream] cake asparagus} :: {and~1 and~2}
```

![ice cream and~1 cake and~2 asparagus](multicoord.0.png)
**Multiword conjunctions.** Correlative conjunctions (<i>either...or</i>, *both...and*, etc.) and expressions like *as well as* are treated as multiwords:

> You may bring either food or drink , as well as a gift .

```bash
$o :: {food drink} :: {[either or]}
$a :: {$o (a > gift)} :: {[as well as]}
You > may < bring < $a
```


## Verb complexes

**Modals and other auxiliaries are roots/heads—main verbs aren’t.**  The two possibilities we considered are “Stanford Dependency/LFG”-style and “Chomsky”-style.  We are using the second style: the first auxiliary/modal is the root, and the main verb depends on it.  Multiple verbs create a chain.  The subject on the left connects to the first verb, while the last verb gets the object.

- `Ingrid > did < have < it`

- `Ingrid > would < have < been < there`

- `Ingrid > (did < not) < have < it`

- `Ingrid > didnt < have < it`

**Infinitival _to_** is treated as the **head** of its non-finite verb:

    I > will < try < to < (love < you) < more

**Quasi-modals** are usually decomposed:

    have < to < announce
    ought < to < announce
    would < like < to < announce
    (would < rather) < announce


## Rooted fragments & discourse issues

`**` serves as an optional top-level root marker. It is usually implicit, but can be provided to require that an expression *not* be headed by any word in the sentence.

Though we have been calling the input a “sentence,” depending on the annotation project it may not be a linguistic sentence. The input may contain multiple “utterances,” which we use loosely to mean any unit that ought to form its own fragment in the full analysis. Interjections and emoticons can be considered separate utterances. If multiple utterances are present in the input, the head of each—typically the verb—should be marked with `**`.

In a full (not underspecified) analysis, every utterance will be a directed subtree (possibly with additional undirected links), with its head attached to the special node `**`.

**Discourse connectives.** “And …,” “though”, “however,” “first of all,” etc. are treated as independently rooted elements if they are kept in the analysis at all.

**Null copula constructions.** If there is no copula, the predicate nominal/adjective generally heads the utterance:

> she the same size as the bop

    she > size

**Sentence-level adverbs.** “Obviously,” “fortunately,” “probably,” and the like (which convey the speaker’s attitude towards the content of the clause) should head the clause they apply to:

> She is **obviously** going to win .
> **Obviously**, she is going to win .

    obviously** < (She > is < going < to < win)

> she **probably** the same size as the bop

	she > size > probably**
	{the same} > size < as < (the > bop)


## Existentials

Existential *there* counts as a subject:

    There > are < {cookies (in < (my > office))}

## Anaphora and Relative Clauses

GFL supports special **undirected node-node relations** for explicit anaphora. Consider this example:

> The police arrested the man who robbed our bank.

    The > police > arrested < man
    the > man < robbed
    who > robbed < (our > bank)
    who = man

![The police arrested the man who robbed our bank.](police.0.png)


Nonrestrictive relative clauses (*The police arrested the man, who robbed our bank*) are analyzed like their restrictive counterparts.

Sometimes the relative pronoun is the object of a preposition, which may be stranded or fronted:

> He is the guy **who** I worked **with**.

    He > is < (the > guy < worked)
    I > worked < with < who
    who = guy

> He is the guy **with whom** I worked.

    He > is < (the > guy < worked)
    I > worked < with < whom
    whom = guy


If there is no overt relative pronoun, the head of the relative clause is attached with a directed arc. Compare:

> She is the one whom/that/∅ I like.

    she > is < (the > one)
    one < (I > like)

plus

- **whom:**

        like < whom
        whom = one

- **that:**

        like < that
        that = one

- **∅:** (no additional annotation fragments)

**Appositives.** Appositives/certain parentheticals are dependents of a nominal head, *and also* anaphorically linked to it: (NOTE: In some instances, noun-noun compounds may be confusable with appositives. The general diagnostic is that apposition is the placement of two complete NPs next each other, while noun-noun compounding is the use of one noun to modify another.)

> Bob , the CEO , was dissing ice cream ( my favorite dessert ! ) .

    Bob > was > dissing < [ice cream]
    Bob < (the > CEO)
    [ice cream] < (my > favorite > dessert)
    Bob = CEO
    [ice cream] = dessert

> Your friend Brainerd is in trouble.

    (Your > friend < Brainerd) > is < [in trouble]
    friend = Brainerd

***Do-* and *so-* anaphora.** These have a verbal antecedent:

> Ingrid likes cheese and so does Brendan .

```bash
Ingrid > likes < cheese
Brendan > [so does]
$a :: {likes [so does]} :: {and}
[so does] = likes
```

## Possessives and predeterminers

The possessive *’s* clitic (if tokenized) is the head of the noun phrase that precedes it. A predeterminer modifies the noun phrase head:

> all the king ’s horses

    all > (the > king > ’s > horses)

