These are abridged guidelines. The full guidelines, if you should come across complex cases are available at:
https://github.com/brendano/gfl_syntax/blob/master/guidelines/guidelines.md

Edges
=====
Use angled brackets ('<', '>') to mark a dependency edge. The bracket should point FROM the dependent TO the head.
```
My > cat > is < grey 
```
If you are not familiar with Dependency syntax, an easy way to think of this is that words which are modifying are dependents to the words they modify. Finite verbs are generally heads of sentences and clauses. Prepositions are heads of prepositional phrases. The subject and objects of verbs are dependents of the verb. Adjectives, adverbs and determiners are dependents of the things they modify.

Coordination
============
There is a special syntax for declaring coordination nodes.
```
"The cat and dog are grey"

The > cat
$x :: {cat dog} :: {and}
$x > are < grey
```
The $x can be anything that starts with a $, and multiple coordination nodes can appear. Also there can be more items in the brackets, eg: $a :: {cat dog elephant} :: {and or} is valid.

Equivalence
===========
There are always multiple equivalent ways to write something in GFL. Some prefer to annotate on one line, some prefer equivalent annotations across multiple lines.
```
My > cat > is < grey
----
is < {grey cat}
cat < My
----
My > cat
cat > is
grey > is
```
The curly braces used above indicate that all of the items enclosed individually attach to is.

Multiwords
==========
Multiword units are enclosed in square brackets. This includes proper names, and words whose meaning is idiomatic when combined. If a multiword unit has internal syntactic structure which is clearly obvious, it is best to indicate it rather than mark it as a multiword.
```
[The United States of America] > is < in < [North America]
```
Parentheses
===========
Parentheses can be used to group things together for the parser. The head of the entire contents of an expression in parentheses will be attached along with everything under it.
```
In < (the > forest)
```
Here, 'the' is a dependent of 'forest' which in turn is a dependent of 'In'. This could also be written without parentheses.
```
the > forest
In < forest
```

Relative Clauses
================
The verb is the head of the relative clause, and the relativizer is probably an argument of that verb.
```
The man who won the car

The > man < won
who > won < (the > car)
```

Verbs
=====
A finite verb is the head of a chain of auxiliary and other verbs.
```
I > would < have < been < being < fed
```

Multiple Roots
==============
Some sentences may have elements which are separately rooted from the rest of the sentence. Discourse connectives and other similar phenomena are common examples of this. If an element of a sentence cannot be easily fit into the syntax of the rest of the sentence you can mark the head of each element with '**'.
```
Anyways , on the other hand , I don't know

Anyways**
on** < ({the other} > hand)
I > don't** < know
```

Training Set
============
Try out the training set and compare your graphs to the examples. There are sometimes multiple possible parses, so the examples represent only one of those. 
