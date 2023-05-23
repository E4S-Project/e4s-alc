How it works
===========

In order to pull, manipulate and save customised images, **E4S A-La-Carte** interacts with a container technology's daemon.

It does so by interpreting the instructions given by the user, whether through it's command line interface or a configuration file, translating these into a succession of shell commands.

After running these commands in an instance of the initial image, we commit the modified image to a new one, ready to be used.
