import sys
import click
from .create import create
from .add import add
from .list import list

# ==========
# Home Group
# ==========

home_options = {
  'create':  'Create a new docker image',
  'list':    'List e4s-alc images',
  'add':     'Add spack packages to a docker image',
  'version': 'The current version of the e4s-alc runtime'
}

class HomeGroup(click.Group):
    def format_help(self, ctx, formatter):
        click.echo('Python Version: {}'.format(sys.version))
        click.echo()
        click.echo('\te4s-alc is the CLI for interacting with docker images and spack packages', nl=False)
        click.echo()
        click.echo()
        self.format_usage(ctx, formatter)
        click.echo()
        self.format_options(ctx, formatter)

    def format_usage(self, ctx, formatter):
        click.echo('Usage:')
        click.echo('  e4s-alc [commands]')

    def format_options(self, ctx, formatter):
        click.echo('Commands:')
        for option, option_desc in home_options.items():
            click.echo('  {:18}{}'.format(option, option_desc))

@click.group(cls=HomeGroup)
def entry():
    pass

@entry.command()
def license():
    click.echo('License:')

@entry.command()
def version():
    click.echo('Version: 0.0.13')

entry.add_command(create)
entry.add_command(add)
entry.add_command(list)
