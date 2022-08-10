Trill is a Troll interpreter

Implemented in Python both as a package and for command line use.

Troll is a dice roll language made by Torben Mogensen  
http://hjemmesider.diku.dk/~torbenm/Troll/


## Command line usage

Rolling a single die: `trill d12`

Rolling multiple die: `trill 3d6`

## Running tests

From the `src` folder: 

`python -m pytest ../tests`


## Development

Currently in a very early state.
Most of the notation is not yet implemented.
See the list below for what is, and what is not (supposed) to work yet. 

### Notation

(From summary on quick reference http://hjemmesider.diku.dk/~torbenm/Troll/quickRef.html)

- [x] roll one dn (1 - n)
- [x] roll m dn
- [x] roll one zn (0 - n)
- [x] roll m zn
- [x] arithmetic on single value (+ - * / mod)
- [x] _sgn_, sign of number
- [x] _sum_, add up values in collection
- [x] _count_ values in collection
- [x] Union of collections (U or @)
- [x] Union of elements { }
- [x] _min_ and _max_ in collection
- [x] all _minimal_ and all _maximal_ values in collection
- [ ] _median_ value in collection
- [ ] _least_ n and _largest_ n values in collection
- [ ] m samples of e ( # )
- [x] range of values ( .. )
- [x] _choose_ value from collection
- [x] _pick_ n values from collection e
- [x] filters (< <= > >= = =/=)
- [x] _drop_ elements
- [x] _keep_ elements
- [ ] multiset difference ( -- )
- [ ] remove duplicates ( _different_ )
- [ ] conditional ( if-then-else )
- [ ] probability ( ?p )
- [ ] logical and ( & )
- [ ] logical not ( ! )
- [ ] bind x to value of e1 in e1 ( _x := e1; e2_ )
- [ ] _foreach x in e1 do e2_
- [ ] _repeat x := e1 while/until e2_
- [ ] _accumulate x := e1 while/until e2_
- [ ] _function_
- [ ] _compositional_
- [ ] _call_
- [ ] text box of single sample ( ' )
- [ ] text box of n samples ( n ' )
- [ ] combine text boxes horisontally ( || )
- [ ] combine text boxes vertically, left-aligned ( |> )
- [ ] combine text boxes vertically, right-aligned ( <| )
- [ ] combine text boxes, centre-aligned ( <> )
- [ ] Pair of e1,e2 ( [e1, e2])
- [ ] First component of pair  ( %1 )
- [ ] Second component of pair ( %2 )
- [ ] x~v returns value of x if x is defined, else returns v
