# xPilot

After installing [pypilot](https://github.com/pypilot/pypilot) on my motorboat (yep, with a little
tweaking, this works fine for motorboats, too), I wanted to have an option to control the steering
with a gamepad.

As I'm on the rhine, steering by course or wind is not an option for me, the only thing I can use is
following a GPS route. But sometimes, it's just too crowded or you cannot predict the path you want
to take. As I had a spare Logitech F710 lying around, I tried to write a little tool which
translates the analog stick into steering movements.

This works more or less, it's definitely to be improved. I did not yet fully understand pypilot and
need another summer session to make it more precise. And yep, the code is horrible but it's a just
for fun project, and it works (on my machine) :D

## Demo

This was the first iteration of it (Maz '22), it's way more sensitive now and does not make such
abrupt movements anymore. But see
yourself: [Demo Video](https://1drv.ms/v/s!ApTlIRJaAWv_hIA4U85A6o8t-TlFZw?e=KrNYF5)

## Note

This was built with the pypilot version beeing shipped
with [OpenPlotter](https://github.com/openplotter) mid 2021. As I directly talk to the pypilot
python API, this might not be compatible with the recent version anymore. I will update this as soon
as it's nt compatible with OpenPlotter (and it's pypilot version) anymore. 
