# 100 Prisoners

## Problem Description

100 prisoners are imprisoned in solitary cells. Each cell is windowless and
soundproof. There's a central living room with one light bulb; the bulb is
initially off. No prisoner can see the light bulb from his or her own cell.
Each day, the warden picks a prisoner equally at random, and that prisoner
visits the central living room; at the end of the day the prisoner is
returned to his cell. While in the living room, the prisoner can toggle the
bulb if he or she wishes. Also, the prisoner has the option of asserting the
claim that all 100 prisoners have been to the living room. If this assertion
is false (that is, some prisoners still haven't been to the living room), all
100 prisoners will be shot for their stupidity. However, if it is indeed
true, all prisoners are set free and inducted into MENSA, since the world can
always use more smart people. Thus, the assertion should only be made if the
prisoner is 100% certain of its validity.

Before this whole procedure begins, the prisoners are allowed to get together
in the courtyard to discuss a plan. What is the optimal plan they can agree on,
so that eventually, someone will make a correct assertion?

## Strategies

### _CounterStrategy_

1 counter, 99 incrementers (can count to 1).

#### Performance

~100 visits from the counter, takes ~10,000 days

### _DayCounterStrategy_

1 counter, 99 incrementers (can count to 2)

the day contains an extra bit of parity. The prisoners have to maintain the
parity of the day by either taking or returning a bit to the chalice.

#### Performance

~700 visits from the counter, takes ~70,000 - 100,000 days

### _RandomCounterStrategy_ 

1 counter, 99 incrementers (can count to 2)

If an incrementer has used up their value, they are allowed to take a value
from the room and place it in the room later.

#### Performance

Same performance as the DayCounter

### _EraCounterStrategy_ 

1 counter, 99 co-counters (can count to arbitrary amounts)

as time goes on, the value of the chalice goes up.  Prisoners try to maintain
parity for the era and hold increasing amounts of temporary information. This
allows the counter to count in large increments (potentially 16 or 32). Every
so often, there is a 'drainage' period, where individuals can flip the chalice
for lower values.

#### Performance

50 visits from counter, ~5000 days in total
