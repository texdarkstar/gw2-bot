# Example usage:

```python
from time import sleep
from bot import Robot


class MyBot(Robot):
    def init(self):
        self.add_trigger(
            regex=r"^You .*, '(.*)'$",
            func=self.my_func,
            name="my_func",
            gag=True,
            )

    def my_func(self, robot, string, matches):
        print "Matched: %s" % string


    def do_something_once(self, robot, timer):
        self.execute("say Hello world")
        self.execute("say Hello again!")
        
        
    def do_something_lots(self, robot, timer):
        self.execute("say my timer ran %d time%s!" % (timer.runs, "s" if timer.runs > 1 else ""))

        
bot = MyBot("username", "password")


bot.connect()
sleep(2)

bot.add_timer(1, bot.do_something_once)
bot.add_timer(.1, bot.do_something_lots, max_runs=10)

bot.execute("finger %s" % bot.username)
bot.loop()
```

# Known quirks:
* The bot will not fire any triggers or write anything to the screen until you call its `loop()` function, which blocks the calling thread.

# Tips on usage:
* If you want to run a single script but use multiple Robots, you will need a structure like so:
```python
from bot import Robot
import threading


def start(bot):
    bot.loop()


def main():
    threads = []
    characters = {"GuyOne": "hispass", "GuyTwo": "hispass"}
    for name in characters:
        bot = Robot(name, characters[name], silent=True)  # Likely will want to set silent=True, otherwise you're gonna get the
        bot.connect()                                     # mud output for each guy written to the same screen.
        thread = threading.Thread(target=start, args=(bot,))
        thread.start()
        threads.append(thread)
main()

```
