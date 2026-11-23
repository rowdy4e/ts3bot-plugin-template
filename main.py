import json, os

import ts3bot   # the bot's side: its tools, the web through it, the settings, why this run was started

city = ts3bot.setting("city", "Praha")                     # a setting (SVC_CITY)
state_file = "/data/state.json"                            # the only writable place that lasts
state = json.load(open(state_file)) if os.path.exists(state_file) else {}

page = ts3bot.fetch(f"https://api.example.com/weather?city={city}")   # only hosts listed under may.fetch
if page.ok:
    ts3bot.tool("say_channel", text=f"[b]{city}[/b]: {page.json()['summary']}")   # only tools listed under may.tools

json.dump(state, open(state_file, "w"))
# Whatever it prints goes to people (the admins on a cron run, whoever typed its !command): print nothing when
# there's nothing to say. An error (an exception, a non-zero exit) is reported to the admins once.
