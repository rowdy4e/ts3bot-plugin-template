# ts3bot-plugin-template

Šablona pluginu pro TeamSpeak bota. **Každý plugin je samostatné repo** `ts3bot-<název>` s `ts3bot.yml` v kořeni;
nainstalovaný plugin je na botovi **služba**. Bot si ho stáhne přímo z GitHubu, nic se nekopíruje ručně a bot se
kvůli tomu nerestartuje.

Nový plugin: na GitHubu **Use this template** → repo pojmenuj `ts3bot-<název>` → vyplň `ts3bot.yml` a `main.py` →
přidej repu téma (topic) `ts3bot-plugin`, ať ho lidi na GitHubu najdou. Bot žádný seznam nečte - instaluje to, co
mu dáš: adresu repa (jako import eggu).

## Instalace (v TeamSpeaku, soukromá zpráva botovi)

```
!service install github.com/rowdy4e/ts3bot-badges
                                       ukáže, co plugin dělá a co smí, zeptá se - a až po tvém „ano“ ho nainstaluje a jednou spustí
!service install github.com/rowdy4e/ts3bot-badges notify=me,Tisi
                                       … rovnou s nastavením
!service list                          co je nainstalované
!service info badges                   co smí, jak je nastavený, odkud je
!service set badges notify me          změna nastavení (none = smazat)
!service update                        které služby mají novější verzi
!service update badges                 ukáže, co se mění (hlavně co smí nově), zeptá se; když nová verze neprojde
                                       prvním během, zůstane stará - i s daty
!service rollback badges               zpátky na předchozí verzi
!service schedule cs2-news 0 * * * *   vlastní rozvrh místo toho z pluginu (default = zpátky)
!service public dice on                jeho !příkaz smí každý s oprávněním „skills“, i v kanálu
!service remove badges                 odebere ho i s nastavením a daty - zeptá se
!service off badges · on · run
```

`!plugin` je totéž co `!service`. Plugin se instaluje vždycky z adresy repa na GitHubu (veřejného):

```
!service install github.com/<účet>/<repo>                 plugin (ts3bot.yml v kořeni repa)
!service install github.com/<účet>/<repo>@v1.2            konkrétní verze (tag, větev, commit)
!service install github.com/<účet>/<repo>/<složka>        …nebo plugin ve složce většího repa
```

…nebo odkaz zkopírovaný z prohlížeče (`https://github.com/<účet>/<repo>`). Totéž jde říct
botovi normální větou („nainstaluj github.com/rowdy4e/ts3bot-badges a piš to mně a Tisimu“) - AI instalaci jen připraví, potvrdit ji musíš ty.

## Kostra pluginu

```
ts3bot-muj-plugin/        (repo)
├── ts3bot.yml      co to je, kdy běží, co smí, jaká má nastavení (povinné)
├── main.py         co se spouští (nebo main.sh) - další soubory vedle něj se vezmou s sebou
├── vendor/         čistě pythonové balíčky, které potřebuje (volitelné)
└── README.md       pro lidi; skryté soubory (.github/, .gitignore) bot nestahuje
```

Tohle repo je ta kostra. Nejmenší příklad je [`ts3bot-dice`](https://github.com/rowdy4e/ts3bot-dice).

### ts3bot.yml

```yaml
name: muj-plugin                  # název služby (povinné)
description: Co dělá, jednou větou.
version: 1.0.0                    # ukazuje se při instalaci a aktualizaci
run: main.py                      # co se spouští (výchozí main.py / main.sh)

when:                             # kdy běží - jeden program, víc důvodů (zjistí ho z TS3BOT_TRIGGER)
  cron: "*/15 * * * *"            # podle rozvrhu (místní čas)
  command: mujplugin              # na !mujplugin [slova]
  join: true                      # když se někdo připojí
  # always: true                  # nebo pořád (nejde s ostatními)

may:                              # všechno, co smí - nic jiného; admin tenhle seznam vidí a potvrzuje
  fetch: [api.example.com]        # weby, které smí číst (přes bota); "*.example.com" = subdomény
  tools: [say_channel, message_user]   # co smí v TeamSpeaku (správu služeb, oprávnění a bota nikdy)
  # network: true                 # skutečné síťové připojení místo fetch (jen z důvěryhodných zdrojů)

settings:                         # vlastní nastavení → proměnná SVC_<KLÍČ>
  mesto: pro jaké město
  notify:
    type: people                  # lidi - bot ukládá jen jejich UID (jméno si může dát kdokoli)
    description: komu psát
    # required: true              # bot se na ně zeptá ještě před instalací
  # apikey: {type: secret, description: klíč k API}   # už se nikdy neukáže
  # limit: {type: number, description: kolik, default: 5}
```

Klíč, který bot nezná, je chyba (s nápovědou) - překlep tak nikdy potichu neznamená něco jiného.

## Co má plugin k dispozici

- **Bota a web - obojí přes bota.** Kontejner pluginu nemá žádnou síť. V Pythonu:

  ```python
  import ts3bot
  ts3bot.tool("say_channel", text="ahoj")              # nástroj z may.tools → odpověď bota (chyba = ts3bot.BotError)
  page = ts3bot.fetch("https://api.example.com/x")     # jen weby z may.fetch → .status .ok .text .content .json()
  ts3bot.setting("mesto", "Praha")                     # nastavení
  ts3bot.people("notify")                              # nastavení typu people → seznam UID
  ts3bot.trigger                                       # cron | command | join | install | manual | always
  ts3bot.args, ts3bot.user_uid, ts3bot.user_name       # co bylo za !příkazem a kdo ho napsal / kdo se připojil
  ```

  V bashi `ts-tool say_channel '{"text": "ahoj"}'` a `ts-fetch https://…`. V čemkoli jiném totéž přes HTTP na unix
  socketu `$TS_BOT_SOCK` s hlavičkou `X-Bot-Token: $TS_BOT_TOKEN`: `POST /tool/<nástroj>` (JSON s argumenty) a
  `POST /fetch` (`{"url": "…"}`) - viz [`ts3bot-docker-hello`](https://github.com/rowdy4e/ts3bot-docker-hello).
- **`/data/`**: jediné místo, kam smí zapisovat; přežije další běhy, restart bota i aktualizaci pluginu.
- **Výstup** (`print`) jde lidem: při běhu podle rozvrhu adminům, na příkaz tomu, kdo ho napsal. Když není co
  říct, nic nevypisuj.
- **Lidi jsou UID**, ne jména: `message_user` bere UID jako `name`.
- **Limity**: 2 minuty, 256 MB a půl jádra na běh; odpověď z webu nejvýš 5 MB, 60 dotazů za minutu.

## Balíčky a jiné jazyky

Na serveru se nikdy nic nesestavuje ani neinstaluje.

- Standardní knihovna Pythonu stačí na hodně (RSS, JSON, regexy…).
- Čistě pythonový balíček přibal: `pip install --target vendor <balíček>` a složku `vendor/` commitni.
- Cokoli jiného (Go, Rust, Node, balíčky s binárkami): vlastní image. Dej do repa `Dockerfile`, do `ts3bot.yml`
  napiš `image: ghcr.io/<účet>/<repo>:<verze>` - workflow [`.github/workflows/images.yml`](.github/workflows/images.yml)
  ho na GitHubu sestaví a nahraje (po prvním nahrání nastav balíček na GitHubu jako veřejný). Bot si ho stáhne, zapamatuje si přesně, který to byl, a pouští jen ten. Vlastní
  image smí jen pluginy z důvěryhodných zdrojů.

## Bezpečnost

- **Vždycky se ptá člověk.** Bot ukáže, co plugin dělá, kdy běží, které weby smí číst a co smí v TeamSpeaku - a
  nainstaluje ho až po „ano“ od toho, kdo instaluje. Žádný přepínač otázku nepřeskočí. AI ji může jen připravit
  (stránka, kterou AI čte, tak nikdy nic nenainstaluje) - i to, co AI sama napíše, potvrzuješ stejně.
- **Sandbox.** Každý běh je zamčený kontejner: nevidí server ani jeho soubory, nemá porty a nemá síť. Na web jen
  přes bota a jen na weby ze svého seznamu - nedostane se tedy ani na jiné služby na tomtéž serveru.
- **Nikdy víc než ty.** Plugin smí jen nástroje ze svého seznamu, a i z nich jen ty, které smí ten, kdo ho
  nainstaloval. Nástroje na správu služeb, oprávnění, AI a bota samotného nedostane nikdy.
- **Důvěryhodné zdroje.** Z účtů v `PluginsTrusted` v konfiguraci (výchozí `github.com/rowdy4e/`), smí plugin přinést i vlastní image nebo chtít skutečné síťové připojení. Odjinud jen skript, a bot
  upozorní, že zdroj není důvěryhodný.
- **Aktualizace na zkoušku.** Nová verze se uloží vedle staré; když neprojde prvním během, vrátí se stará včetně
  dat. Vypnutá služba zůstane vypnutá. Nastavení a data převezme jen nová verze **téhož** pluginu - jiný plugin se
  stejným jménem začíná načisto.

## Pluginy

| Repo | Co dělá |
|---|---|
| [ts3bot-badges](https://github.com/rowdy4e/ts3bot-badges) | Hlídá nové TeamSpeak badges a jejich kódy (oficiální seznam + vlákno na fóru); do kanálu, nebo soukromě vybraným lidem podle UID - hned, jak se připojí. |
| [ts3bot-cs2-news](https://github.com/rowdy4e/ts3bot-cs2-news) | Nové články o CS2 ze Steamu do kanálu. |
| [ts3bot-dice](https://github.com/rowdy4e/ts3bot-dice) | Nejmenší plugin: `!roll` v bashi. |
| [ts3bot-docker-hello](https://github.com/rowdy4e/ts3bot-docker-hello) | Ukázka pluginu ve vlastním Docker image. |
