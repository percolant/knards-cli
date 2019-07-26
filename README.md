### knards-cli: (TODO)
CLI version of knards

### available commands: (TODO everywhere)
`$ kn --help`
Shows general help
(same to any subcommand)

`$ kn bootstrap`
Creates a new DB if there's none with the set up name within the set up path, look up `config.py` for settings.

`$ kn list`
Lists all created cards.

`$ kn list --inc="multiword marker,python" --exc=javascript,c++`
Lists all cards that (must) have markers "multiword marker" and "python", and (must) not have markers "javascript" and "c++".

`$ kn list --no-q --inc=languages,english`
Lists all cards that have markers "languages" and "english", don't output questions (only answers; default is both)

`$ kn list --no-a`
Lists all created cards, don't output answers (only questions)

`$ kn new`
Prompt for new card creation, start with question by default.
This is the same as: `$ kn new --qf`

`$ kn new --af`
Prompt for new card creation, start with answer.

`$ kn copy --m=python`
Copy last created card that has marker "python".
Also, you may specify question/answer to be prompted first: `$ kn copy --m=python --af` (default is `--qf`)

`$ kn del --id=1`
Delete card with id 1.

`$ kn del --m=python`
Delete all cards that have marker "python".

`$ kn edit --id=1`
Edit card with id 1.
Also, you may specify question/answer to be prompted first: `$ kn edit --id=1 --af` (default is `--qf`)

`$ kn status`
Show how many cards are ready to be revised.

`$ kn status --inc="multiple words,python" --exc=c++`
Show how many cards with markers "multiple words" and "python" and without marker "c++" are ready to be revised.

`$ kn status --t`
Show how many cards were already revised today.

`$ kn rev`
Start revising cards.

`$ kn rev --inc="multiple words,python" --exc=c++`
Start revising cards that have markers "multiple words" and "python" and don't have marker "c++".
