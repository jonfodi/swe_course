## data structure learning + real system building 

# building a cyber data processing system 
thinking of questions cyber people wanna know and the resulting access patterns 
then the ds + a that make these efficient 
goal is for each question to motivate a new ds + a 
- but also want to demonstrate the same ds used for different a depending on what data we need 

# lenses im using to solve/optimize these problems 
what ds do we need to solve this?
- totally feasible to use multiple like in q1. building a intermediate structure to make the problem easier 
- also super useful to create ds at write time that will save query time 
    - like in q2 when creating the hash map avoids the need to loop through the whole list 

## useful stuff 
# bisection
used for filtering lists 

bisect_left(a, x) = first index where a[i] >= x --> cutoff included
bisect_right(a, x) = first index where a[i] > x --> cutoff excluded

return len(a) - bisect(a, cutoff)


# ultimate goals 
- decompose real world app questions into ds + a problems 
- learn the uses of the common data strucutres 
    - HM, graph, stack, queue, heap, LL? 
- map algorithms to app level data access questions 
- build a generic data fetcher (DB)
    - everything well have built will be bespoke for the cyber application. optimized for the exact query but hard to maintain 
    - use this motivation to build a generic fetcher that loses the perofrmance but greatly simplifies the maintenance 


# todo 
- different algos on the HM 
- new DS 
    - graph, stack? queue? idek 
