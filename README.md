# Tshivenda Bot

A command line bot for learning, translating and preserving Tshivenda.

## What it does

1. **Translation** both ways between English and Tshivenda, with phrase matching, not just single words
2. **Dictionary** with multiple senses per word, part of speech, category and notes
3. **Quizzes** generated automatically from the dictionary, so they grow as the dictionary grows
4. **Drill mode** using spaced repetition, which brings back the words you get wrong
5. **Riddles, proverbs and jokes** (thai, mirero, zwiseo)
6. **News** from Limpopo, cached so it still works offline
7. **Culture and history** notes on Venda
8. **Contribution tools** so speakers can add and verify entries from inside the bot

## Install

```
git clone https://github.com/MbakzArr/Python_Tshivenda_Bot.git
cd Python_Tshivenda_Bot
python -m venv venv
```

Windows:
```
venv\Scripts\activate
```

Linux or macOS:
```
source venv/bin/activate
```

Then:
```
pip install -r requirements.txt
```

## Three ways to run it

```
python bot.py                terminal
python bot.py --web --open   web page, opens your browser
python bot.py --gui          desktop window
```

All three share one engine, so a word added in the browser shows up in the
terminal straight away. The web page and the desktop window need no extra
packages at all. Everything runs on your own machine and nothing you type
is sent anywhere.

The web page loads two fonts from Google, including Gentium Book Plus which
SIL drew to carry the marks under Tshivenda letters. If you are offline or on
a slow connection it falls back to system fonts and still works.

The desktop window needs tkinter. It ships with Python on Windows and macOS.
On Ubuntu or Debian: `sudo apt install python3-tk`.

Only `requests` and `beautifulsoup4` are needed, and those are only for the
news feature. Everything else runs on the standard library.

## Terminal commands

| Command | What it does |
| --- | --- |
| `/help` or `/thusa` | list every command |
| `/translate <text>` or `/t` | translate, direction detected automatically |
| `/define <word>` or `/d` | every meaning of a word, with notes |
| `/search <text>` | find any entry containing that text |
| `/word` | word of the day |
| `/quiz [n] [category]` | multiple choice quiz, for example `/quiz 10 body` |
| `/learn [n]` | spaced repetition drill on your weak words |
| `/riddle` or `/thai` | a Tshivenda riddle |
| `/proverb` or `/murero` | a Tshivenda proverb |
| `/joke` | a joke |
| `/news` | a full article from Limpopo Mirror |
| `/headlines` | recent headlines only |
| `/about <topic>` | culture and history |
| `/history`, `/geography` | detail on the Venda territory |
| `/add [word\|riddle\|proverb\|joke]` | teach the bot something new |
| `/review [n]` | confirm or correct unverified entries |
| `/stats` | dictionary size and your learning progress |
| `/categories` | list dictionary categories |
| `ndi zwone` | leave |

Anything typed without a slash is treated as a translation request, so you can
just type `ndi khou toda madi` and get an answer.

You can also run a single command without entering the loop:

```
python bot.py /define duvha
```

## How the dictionary is built

One entry is one **sense**, not one word. This is what solves the problem noted
in the old `dataset/todo` file:

```
duvha = day
duvha = sun
thambo = rope
thambo = invitation
```

Those are four separate entries. Looking up `duvha` returns every meaning with
its note, instead of one meaning silently overwriting the other.

An entry looks like this:

```json
{
  "id": "e0122",
  "en": "day",
  "ve": "duvha",
  "pos": "noun",
  "category": "time",
  "context": "",
  "note": "same word as sun, context decides",
  "alt": [],
  "review": true
}
```

`review: true` means no first language speaker has confirmed it yet. The bot
says so when it shows you the entry. Use `/review` to work through the list.

### Diacritics

Tshivenda uses letters carrying a mark underneath. The bot stores whatever you
type but strips the marks when matching, so `duvha` and the properly marked
spelling both find the same entry. Adding correct spelling later will not break
anything already in the file.

## Project layout

```
bot.py              entry point, command table, --web and --gui flags
gui.py              desktop window, tkinter
web/
  server.py         web server, standard library only
  static/index.html the whole web interface, one file
core/
  api.py            shared service layer every interface calls
  text.py           folding, diacritic stripping, language detection
  lexicon.py        dictionary loading, indexing, search, adding
  translate.py      translation engine
  quiz.py           question generation
  learn.py          spaced repetition and progress
  content.py        riddles, proverbs, jokes, culture
  news.py           scraping with caching and timeouts
  history.py        Venda territory data
  ui.py             terminal colours
data/               all content as JSON
tools/
  migrate.py        old response.json to the new lexicon
  rebuild.py        full rebuild in one command
  seed_core.py      high frequency word pack
tests/              pytest suite
userdata/           your progress and news cache, not committed
```

## Rebuilding the dictionary

If you edit `dataset/response.json` and want to regenerate:

```
python tools/rebuild.py dataset/response.json data/lexicon.json
python tools/seed_core.py data/lexicon.json
```

## Tests

```
pip install pytest
python -m pytest tests/ -q
```

## The data problem

The code is no longer the limit on this project. The dictionary is. Around 330
entries covers greetings, body parts, family and common phrases, but not enough
verbs, tenses or noun classes to translate a real sentence cleanly.

Two things move it forward:

1. `/add` and `/review`, so every session a speaker uses the bot makes it better
2. A verified core of a few thousand words, which is where the real work sits

Entries marked `review: true` have not been checked by a first language speaker
and should be treated as drafts.

## Contributing

Open an issue or a pull request. Corrections to Tshivenda spelling and meaning
are the most useful contribution.

## License

MIT
