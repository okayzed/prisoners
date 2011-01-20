# 100 prisoners are imprisoned in solitary cells. Each cell is windowless and
# soundproof. There's a central living room with one light bulb; the bulb is
# initially off. No prisoner can see the light bulb from his or her own cell.
# Each day, the warden picks a prisoner equally at random, and that prisoner
# visits the central living room; at the end of the day the prisoner is
# returned to his cell. While in the living room, the prisoner can toggle the
# bulb if he or she wishes. Also, the prisoner has the option of asserting the
# claim that all 100 prisoners have been to the living room. If this assertion
# is false (that is, some prisoners still haven't been to the living room), all
# 100 prisoners will be shot for their stupidity. However, if it is indeed
# true, all prisoners are set free and inducted into MENSA, since the world can
# always use more smart people. Thus, the assertion should only be made if the
# prisoner is 100% certain of its validity.

# Before this whole procedure begins, the prisoners are allowed to get together
# in the courtyard to discuss a plan. What is the optimal plan they can agree on,
# so that eventually, someone will make a correct assertion?

import random
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("Dilemma")
log.setLevel(logging.INFO)

from collections import defaultdict

VISITS = []
VISITED = defaultdict(int)

TOGGLE_VALUE = None
NUM_PRISONERS = 100

class Strategy:
  def __init__(self):
    pass

  def simulate(self):
    turns = 0
    TOGGLE_VALUE = False
    while True:
      cur_prisoner = random.randint(1, NUM_PRISONERS)
      VISITED[cur_prisoner] += 1
      log.debug( "BEATING PRISONER #%s" % cur_prisoner)
      log.debug( "%s days" % turns)
      if self.guess(cur_prisoner):
        log.debug( len(VISITED))
        if len(VISITED) >= NUM_PRISONERS:
          log.info( "SUCCESSFUL GUESS")
          return turns
        else:
          raise("INCORRECT! OFF WITH SOME HEADS!")
      turns += 1


# The basic 1 person is a counter strategy.
# They are the only one allowed to flip the
# chalice down, everyone else flips it up.
#
# The counter can count 1 value at a time in this strategy.
class CounterStrategy(Strategy):
  def __init__(self):
    self.COUNTER_INDEX = 1
    self.COUNTER_COUNT = 0
    self.COUNTER_VISITS=defaultdict(int)
    self.DID_TOGGLE = defaultdict(bool)

  def reset(self):
    self.COUNTER_INDEX   =  1
    self.COUNTER_COUNT   =  0
    self.COUNTER_VISITS  =  defaultdict(int)
    self.DID_TOGGLE      =  defaultdict(bool)

  def guess(self, prisoner_number):
    global TOGGLE_VALUE
    if TOGGLE_VALUE:
      if prisoner_number == self.COUNTER_INDEX:
        log.debug( 'Resetting Lightbulb')
        TOGGLE_VALUE = False
        self.COUNTER_COUNT += 1
        log.debug( "%s visits" % self.COUNTER_COUNT)
        if self.COUNTER_COUNT == NUM_PRISONERS - 1:
          return True
    else:
      if prisoner_number == self.COUNTER_INDEX:
        log.debug( "Counter already visited")
      else:
        if not prisoner_number in self.DID_TOGGLE:
          log.debug( 'Setting Lightbulb')
          TOGGLE_VALUE = True
          self.DID_TOGGLE[prisoner_number] = True
        else:
          log.debug( 'Prisoner Already visited')

    self.COUNTER_VISITS[prisoner_number] += 1


# In this strategy, individuals can temporarily store a value and later return
# it to the room if the room is empty. There is still only one counter, but the
# idea is to spread out how often they will see the value.
class RandomCounterStrategy(CounterStrategy):
  def __init__(self):
    CounterStrategy.__init__(self)
    self.TOGGLE_AGAIN = defaultdict(int)

  def guess(self, prisoner_number):
    global TOGGLE_VALUE
    if TOGGLE_VALUE:
      if prisoner_number == self.COUNTER_INDEX:
        log.debug( 'Resetting Lightbulb')
        TOGGLE_VALUE = False
        self.COUNTER_COUNT += 1
        log.debug( "%s visits" % self.COUNTER_COUNT)
        if self.COUNTER_COUNT == NUM_PRISONERS - 1:
          log.debug( "Counter Visits: %s" % (self.COUNTER_VISITS[self.COUNTER_INDEX]))
          return True
    else:
      if prisoner_number == self.COUNTER_INDEX:
        log.debug( "Counter already visited")
      else:
        if not prisoner_number in self.DID_TOGGLE or prisoner_number in self.TOGGLE_AGAIN:
          log.debug( 'Setting Lightbulb')
          TOGGLE_VALUE = True
          self.DID_TOGGLE[prisoner_number] = True
          if self.TOGGLE_AGAIN[prisoner_number] <= 1:
            del self.TOGGLE_AGAIN[prisoner_number]
          else:
            self.TOGGLE_AGAIN[prisoner_number] -= 1

        else:
          if prisoner_number in self.DID_TOGGLE:
            if random.random() > 0.95:
              TOGGLE_VALUE = False
              self.TOGGLE_AGAIN[prisoner_number] += 1
              log.debug( 'Prisoner Already visited')

    self.COUNTER_VISITS[prisoner_number] += 1

# In this strategy, the parity of the day stores an
# extra bit of information. The purpose is to give the
# counter the ability to count up to 2 values at once.
class DayCounterStrategy(CounterStrategy):
  def __init__(self):
    CounterStrategy.__init__(self)
    self.turn = 0
    self.tokens = defaultdict(int)
    for x in xrange(1, NUM_PRISONERS+1):
      self.tokens[x] = 1

  def guess(self, prisoner):
    self.turn += 1
    global TOGGLE_VALUE
    if prisoner == self.COUNTER_INDEX:
      count_add = 0
      if TOGGLE_VALUE:
        TOGGLE_VALUE = False
        if self.turn % 2 == 0:
          count_add = 2
        else:
          count_add = 1

        self.COUNTER_COUNT += count_add
        if self.COUNTER_COUNT == 99:
          return True
    else:
      # Set the lightbulb to tomorrows value
      if TOGGLE_VALUE:
        # If today is a 2day and the light is on, take the extra token back so tomorrow is a 1day
        if self.turn % 2 == 0:
            self.tokens[prisoner] += 1
        else:
          # If today is a 1 day, and the prisoner can make it a 2day
          if self.tokens[prisoner] >= 1:
            self.tokens[prisoner] -= 1
          else:
            self.tokens[prisoner] += 1
            TOGGLE_VALUE = False

      else:
        if self.turn % 2 == 0:
          if self.tokens[prisoner] >= 1:
            self.tokens[prisoner] -= 1
            TOGGLE_VALUE = True
        else:
          if self.tokens[prisoner] >= 2:
            self.tokens[prisoner] -= 2
            TOGGLE_VALUE = True



class Era:
  def __init__(self, *args, **kwargs):
    self.ends_on_turn = None
    self.load_func = None
    self.guess_func = None
    self.name = None

  def is_active(self, turn):
    return self.ends_on_turn > turn or not self.ends_on_turn

  def guess(self, prisoner):
    return self.guess_func(prisoner)

# In the EraCounterStrategy, everyone can be a 'witness'. That means they are
# allowed to witness a chalice sighting and temporarily store the value.
# Instead of them temporarily holding 1 value, though, as time goes on, the
# value of the chalice is increased (era by era). 

# They prisoners allowed to increase it if possible, otherwise, they have to
# retain their value until a 'reset' Era comes, where the value of the chalice
# is reset to 1 again, allowing prisoners to release stored values.

# The idea is to allow the counter to pick up large values at a time.
class EraCounterStrategy(CounterStrategy):
  def __init__(self):
    CounterStrategy.__init__(self)
    self.witnesses = defaultdict(int)
    for x in xrange(1, NUM_PRISONERS+1):
      self.witnesses[x] = 1
    self.givers = {}
    self.turn = 0
    self.era = 0

  def accumulate(self, prisoner, k=1):
    global TOGGLE_VALUE
    if prisoner == self.COUNTER_INDEX:
      return

    if TOGGLE_VALUE:
      if self.witnesses[prisoner] == k:
        TOGGLE_VALUE = False
        self.witnesses[prisoner] += k
    else:
      if self.witnesses[prisoner] >= k:
        TOGGLE_VALUE = True
        self.witnesses[prisoner] -= k

  def count(self, prisoner, k=2):
    global TOGGLE_VALUE
    if TOGGLE_VALUE:
      if prisoner == self.COUNTER_INDEX:
        TOGGLE_VALUE = False
        self.COUNTER_COUNT += k
        log.debug( 'Counting prisoner for %s, %s total, %s' % (k, self.COUNTER_COUNT, self.COUNTER_INDEX))
        log.debug( self.witnesses)
        if self.COUNTER_COUNT >= NUM_PRISONERS - 1:
          return True

#        if NUM_PRISONERS - self.COUNTER_COUNT < 5:
#          self.turn = 10000
    else:
      if self.witnesses[prisoner] >= k:
        TOGGLE_VALUE = True
        self.witnesses[prisoner] -= k
        log.debug( "Prisoner %s setting lightbulb" % prisoner)

  def load_counter(self, prisoner, k):
    self.COUNTER_INDEX = prisoner
    log.debug( "Setting counter index to %s" % (self.COUNTER_INDEX))
    log.debug( "Pre-counting %s" % (self.witnesses[prisoner]))
    self.COUNTER_COUNT += self.witnesses[prisoner]
    self.witnesses[prisoner] = 0

    self.print_era()

  def load_prisoner(self, prisoner, k):
    global TOGGLE_VALUE
    if TOGGLE_VALUE:
      log.debug( "Collecting %s from leftover lightbulb" % (k))
      self.witnesses[prisoner] += k
      TOGGLE_VALUE = False

    self.print_era()

  def print_era(self):
    log.debug( "ERA %s INFO" % (self.era))
    log.debug( self.witnesses)
    vote_counts = sorted(list(set(self.witnesses.values())))
    log.debug("Vote Counts:")
    for vc in vote_counts:
      log.debug("%s: %s" % (vc, len(filter(lambda k: self.witnesses[k] == vc, self.witnesses))))
    log.debug( "Collected in era: %s" % (self.COUNTER_COUNT))

  def guess(self, prisoner):
    eras = []
    e = Era()
    e.ends_on_turn = 500
    e.guess_func = lambda x: self.accumulate(x,1)
    eras.append(e)

    e = Era()
    e.ends_on_turn = 1000
    e.guess_func = lambda x: self.accumulate(x,2)
    e.load_func = lambda x: self.load_prisoner(x, 1)
    eras.append(e)

    e = Era()
    e.ends_on_turn = 1500
    e.guess_func = lambda x: self.accumulate(x,4)
    e.load_func = lambda x: self.load_prisoner(x, 2)
    eras.append(e)

    e = Era()
    e.ends_on_turn = 2500
    e.guess_func = lambda x: self.count(x,8)
    e.load_func = lambda x: self.load_counter(x, 4)
    eras.append(e)

    e = Era()
    e.ends_on_turn = 3500
    e.guess_func = lambda x: self.count(x,4)
    e.load_func = lambda x: self.load_prisoner(x, 8)
    eras.append(e)

    e = Era()
    e.ends_on_turn = 4000
    e.guess_func = lambda x: self.count(x,2)
    e.load_func = lambda x: self.load_prisoner(x, 4)
    eras.append(e)

    e = Era()
    e.guess_func = lambda x: self.count(x,1)
    e.load_func = lambda x: self.load_prisoner(x, 2)
    eras.append(e)

    response = None
    next_turn_initializes = False
    for era in eras:
      if era.is_active(self.turn):
        if next_turn_initializes:
          era.load_func(prisoner)
        response = era.guess(prisoner)
        break

      if self.turn == era.ends_on_turn:
        next_turn_initializes = True
        self.era += 1


    self.COUNTER_VISITS[prisoner] = True
    self.turn += 1

    return response

if __name__ == "__main__":
  turns = []
  all_visits = []
  avgs = []
  for i in xrange(10):
    del VISITS[:]
    VISITED.clear()
    cs = EraCounterStrategy()
    turns.append(cs.simulate())
    avg_visits = (sum(VISITED.values()) / NUM_PRISONERS)
    log.info( "Average Visits: %s" % avg_visits)
    avgs.append(avg_visits)
  avg_turn = sum(turns) / len(turns)
  log.info("Average Stats:")
  log.info( "Days: %s Years: %s Visits: %s" % (avg_turn, avg_turn / 365.0, sum(avgs) / len(avgs)))
