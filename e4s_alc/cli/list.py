import click
import docker

import e4s_alc
from e4s_alc.database.edit import read_all_entries, remove_entry

# ==============
# List Command
# ==============

@click.command()
def list():
    print()
    click.secho('E4S-ALC images:', fg='green')
    print('=' * 40) 

    client = docker.from_env()
    image_tags = set()
    for image in client.images.list():
        for tag in image.tags:
            name_tag_name = tag.split(':')
            name = name_tag_name[0]
            image_tags.add(name)

    seen_entries = set() 
    entries = read_all_entries()
    for entry in entries:
        name, os, packages, date = entry
        if name not in image_tags and os not in image_tags:
            remove_entry(name)
            # Remove entry from db if not in tags

        if (name, os) in seen_entries:
            continue
        seen_entries.add((name, os))

        print('\t{} ({}): - {}'.format(name, os, date))
        if packages:
            for package in packages.split(' '):
                print('\t\t+ {}'.format(package))
        else:
            print('\t\tNo spack packages or spack installed')
        print()
