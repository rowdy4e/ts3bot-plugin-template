# ts3bot-plugin-template

A plugin template for the TeamSpeak bot. **Every plugin is a repo of its own**, `ts3bot-<name>`, with `ts3bot.yml` at
its root; installed on a bot, a plugin is a **service**. The bot downloads it straight from GitHub - nothing is
copied by hand, and the bot doesn't restart for it.

A new plugin: on GitHub **Use this template** → name the repo `ts3bot-<name>` → fill in `ts3bot.yml` and `main.py` →
give the repo the topic `ts3bot-plugin` so people find it on GitHub. The bot reads no list - it installs what you
give it: the repo's address (like importing an egg).

## Installing (in TeamSpeak, a private message to the bot)

```
!service install github.com/rowdy4e/ts3bot-badges
                                       shows what the plugin does and may do, asks - and installs and runs it once
                                       only after your "yes"
!service install github.com/rowdy4e/ts3bot-badges notify=me,Tisi
                                       … with its settings right away
!service list                          what's installed
!service info badges                   what it may do, its settings, where it came from
!service set badges notify me          change a setting (none = clear it)
!service update                        which services have a newer version
!service update badges                 shows what changes (above all what it may newly do), asks; if the new version
                                       fails its first run, the old one stays - data included
!service rollback badges               back to the version before
!service schedule cs2-news 0 * * * *   your own schedule instead of the plugin's (default = back to it)
!service public dice on                its !command is for everyone with the 'skills' right, also in the channel
!service remove badges                 removes it with its settings and data - asks first
!service off badges · on · run
```

`!plugin` is the same as `!service`. A plugin is always installed from a (public) GitHub repo's address:

```
!service install github.com/<account>/<repo>              the plugin (ts3bot.yml at the repo's root)
!service install github.com/<account>/<repo>@v1.2         a given version (tag, branch, commit)
!service install github.com/<account>/<repo>/<folder>     …or a plugin in a folder of a bigger repo
```

…or the link copied from the browser (`https://github.com/<account>/<repo>`). You can also tell the bot in plain
words ("install github.com/rowdy4e/ts3bot-badges and send it to me and Tisi") - the AI only prepares the install,
you confirm it.

## A plugin's skeleton

```
ts3bot-my-plugin/        (the repo)
├── ts3bot.yml      what it is, when it runs, what it may do, its settings (required)
├── main.py         what runs (or main.sh) - other files next to it come along
├── vendor/         pure-Python packages it needs (optional)
└── README.md       for people: README, LICENSE, CHANGELOG and hidden files (.github/, .gitignore) aren't downloaded
```

This repo is that skeleton. The smallest example is [`ts3bot-dice`](https://github.com/rowdy4e/ts3bot-dice).

### ts3bot.yml

```yaml
name: my-plugin                   # the service's name (required)
description: What it does, in one sentence.
version: 1.0.0                    # shown on install and update
run: main.py                      # what runs (default main.py / main.sh)

when:                             # when it runs - one program, several reasons (it reads which from TS3BOT_TRIGGER)
  cron: "*/15 * * * *"            # on a schedule (local time)
  command: myplugin               # on !myplugin [words]
  join: true                      # when someone connects
  # always: true                  # or all the time (not with the others)

may:                              # everything it may do - nothing else; the admin sees this list and confirms it
  fetch: [api.example.com]        # web hosts it may read (through the bot); "*.example.com" = its subdomains
  tools: [say_channel, message_user]   # what it may do in TeamSpeak (never manage services, rights or the bot)
  # network: true                 # a real network connection instead of fetch (trusted sources only)

settings:                         # its own settings → the variable SVC_<KEY>
  city: which city
  notify:
    type: people                  # people - the bot keeps only their UIDs (anyone can take a name)
    description: who to tell
    # required: true              # the bot asks for them before installing
  # apikey: {type: secret, description: the API key}   # never shown again
  # limit: {type: number, description: how many, default: 5}
```

A key the bot doesn't know is an error (with a hint) - so a typo never quietly means something else.

## What a plugin has

- **The bot and the web - both through the bot.** A plugin's container has no network at all. In Python:

  ```python
  import ts3bot
  ts3bot.tool("say_channel", text="hello")             # a tool from may.tools → the bot's answer (error = ts3bot.BotError)
  page = ts3bot.fetch("https://api.example.com/x")     # only hosts from may.fetch → .status .ok .text .content .json()
  ts3bot.setting("city", "Prague")                     # a setting
  ts3bot.people("notify")                              # a people setting → a list of UIDs
  ts3bot.trigger                                       # cron | command | join | install | manual | always
  ts3bot.args, ts3bot.user_uid, ts3bot.user_name       # what came after the !command, and who typed it / connected
  ```

  In bash `ts-tool say_channel '{"text": "hello"}'` and `ts-fetch https://…`. In anything else the same over HTTP on
  the unix socket `$TS_BOT_SOCK` with the header `X-Bot-Token: $TS_BOT_TOKEN`: `POST /tool/<tool>` (JSON arguments)
  and `POST /fetch` (`{"url": "…"}`) - see [`ts3bot-docker-hello`](https://github.com/rowdy4e/ts3bot-docker-hello).
- **`/data/`**: the only place it may write; it outlives runs, bot restarts and plugin updates.
- **Output** (`print`) goes to people: on a scheduled run to the admins, on a command to whoever typed it. When
  there's nothing to say, print nothing.
- **People are UIDs**, not names: `message_user` takes a UID as `name`.
- **Limits**: 2 minutes, 256 MB and half a core per run; at most 5 MB from the web per answer, 60 requests a minute.

## Packages and other languages

Nothing is ever built or installed on the server.

- Python's standard library goes a long way (RSS, JSON, regexes…).
- Bring a pure-Python package along: `pip install --target vendor <package>` and commit the `vendor/` folder.
- Anything else (Go, Rust, Node, packages with binaries): its own image. Put a `Dockerfile` in the repo and write
  `image: ghcr.io/<account>/<repo>:<version>` in `ts3bot.yml` - the workflow
  [`.github/workflows/images.yml`](.github/workflows/images.yml) builds and uploads it on GitHub (after the first
  upload, make the package public on GitHub if it isn't). The bot pulls it, remembers exactly which one it was, and
  runs only that one. Only plugins from trusted sources may bring their own image.

## Security

- **A human always says yes.** The bot shows what a plugin does, when it runs, which sites it may read and what it
  may do in TeamSpeak - and installs it only after a "yes" from whoever is installing. No flag skips the question. The
  AI can only prepare it (so a page the AI reads never installs anything) - and what the AI writes itself, you
  confirm the same way.
- **Sandbox.** Every run is a locked container: it can't see the server or its files, has no ports and no network.
  The web only through the bot and only the sites on its list - so it can't reach other services on the same server
  either.
- **Never more than you.** A plugin may use only the tools on its list, and of those only what the person who
  installed it may use. It never gets the tools for managing services, rights, the AI or the bot itself.
- **Trusted sources.** From the accounts in `PluginsTrusted` in the config (default `github.com/rowdy4e/`), a plugin
  may also bring its own image or ask for a real network connection. From anywhere else only a script, and the bot
  warns that the source isn't trusted.
- **Updates on trial.** A new version is stored next to the old one; if it fails its first run, the old one comes
  back, data included. A service that was off stays off. Settings and data carry over only to a new version of the
  **same** plugin - a different plugin with the same name starts from scratch.

## Plugins

| Repo | What it does |
|---|---|
| [ts3bot-badges](https://github.com/rowdy4e/ts3bot-badges) | Watches new TeamSpeak badges and their codes (the official list + the forum thread); privately to whoever subscribed (`!badges subscribe`) - as soon as they connect - or to the channel. |
| [ts3bot-cs2-news](https://github.com/rowdy4e/ts3bot-cs2-news) | New CS2 articles from Steam, to the channel. |
| [ts3bot-dice](https://github.com/rowdy4e/ts3bot-dice) | The smallest plugin: `!roll` in bash. |
| [ts3bot-docker-hello](https://github.com/rowdy4e/ts3bot-docker-hello) | A plugin in its own Docker image. |
