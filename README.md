#Example usage:

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
