# coding: utf-8
import json
import os
from xml.sax.saxutils import escape


def serialize_json(doujinshi, dir):
    metadata = {'title': doujinshi.name,
                'subtitle': doujinshi.info.subtitle}
    if doujinshi.info.date:
        metadata['upload_date'] = doujinshi.info.date
    if doujinshi.info.parodies:
        metadata['parody'] = [i.strip() for i in doujinshi.info.parodies.split(',')]
    if doujinshi.info.characters:
        metadata['character'] = [i.strip() for i in doujinshi.info.characters.split(',')]
    if doujinshi.info.tags:
        metadata['tag'] = [i.strip() for i in doujinshi.info.tags.split(',')]
    if doujinshi.info.artists:
        metadata['artist'] = [i.strip() for i in doujinshi.info.artists.split(',')]
    if doujinshi.info.groups:
        metadata['group'] = [i.strip() for i in doujinshi.info.groups.split(',')]
    if doujinshi.info.languages:
        metadata['language'] = [i.strip() for i in doujinshi.info.languages.split(',')]
    metadata['category'] = doujinshi.info.categories
    metadata['URL'] = doujinshi.url
    metadata['Pages'] = doujinshi.pages

    with open(os.path.join(dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, separators=','':')


def serialize_comicxml(doujinshi, dir):
    from iso8601 import parse_date
    with open(os.path.join(dir, 'ComicInfo.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')

        xml_write_simple_tag(f, 'Manga', 'Yes')

        xml_write_simple_tag(f, 'Title', doujinshi.name)
        xml_write_simple_tag(f, 'Summary', doujinshi.info.subtitle)
        xml_write_simple_tag(f, 'PageCount', doujinshi.pages)
        xml_write_simple_tag(f, 'URL', doujinshi.url)
        xml_write_simple_tag(f, 'NhentaiId', doujinshi.id)
        xml_write_simple_tag(f, 'Genre', doujinshi.info.categories)

        xml_write_simple_tag(f, 'BlackAndWhite', 'No' if doujinshi.info.tags and 'full color' in doujinshi.info.tags else 'Yes')

        if doujinshi.info.date:
            dt = parse_date(doujinshi.info.date)
            xml_write_simple_tag(f, 'Year', dt.year)
            xml_write_simple_tag(f, 'Month', dt.month)
            xml_write_simple_tag(f, 'Day', dt.day)
        if doujinshi.info.parodies:
            xml_write_simple_tag(f, 'Series', doujinshi.info.parodies)
        if doujinshi.info.characters:
            xml_write_simple_tag(f, 'Characters', doujinshi.info.characters)
        if doujinshi.info.tags:
            xml_write_simple_tag(f, 'Tags', doujinshi.info.tags)
        if doujinshi.info.artists:
            xml_write_simple_tag(f, 'Writer', ' & '.join([i.strip() for i in doujinshi.info.artists.split(',')]))
        # if doujinshi.info.groups:
        #     metadata['group'] = [i.strip() for i in doujinshi.info.groups.split(',')]
        if doujinshi.info.languages:
            languages = [i.strip() for i in doujinshi.info.languages.split(',')]
            xml_write_simple_tag(f, 'Translated', 'Yes' if 'translated' in languages else 'No')
            [xml_write_simple_tag(f, 'Language', i) for i in languages if i != 'translated']

        f.write('</ComicInfo>')


def xml_write_simple_tag(f, name, val, indent=1):
    f.write('{}<{}>{}</{}>\n'.format(' ' * indent, name, escape(str(val)), name))


def merge_json():
    lst = []
    output_dir = "./"
    os.chdir(output_dir)
    doujinshi_dirs = next(os.walk('.'))[1]
    for folder in doujinshi_dirs:
        files = os.listdir(folder)
        if 'metadata.json' not in files:
            continue
        data_folder = output_dir + folder + '/' + 'metadata.json'
        json_file = open(data_folder, 'r')
        json_dict = json.load(json_file)
        json_dict['Folder'] = folder
        lst.append(json_dict)
    return lst


def serialize_unique(lst):
    dictionary = {}
    parody = []
    character = []
    tag = []
    artist = []
    group = []
    for dic in lst:
        if 'parody' in dic:
            parody.extend([i for i in dic['parody']])
        if 'character' in dic:
            character.extend([i for i in dic['character']])
        if 'tag' in dic:
            tag.extend([i for i in dic['tag']])
        if 'artist' in dic:
            artist.extend([i for i in dic['artist']])
        if 'group' in dic:
            group.extend([i for i in dic['group']])
    dictionary['parody'] = list(set(parody))
    dictionary['character'] = list(set(character))
    dictionary['tag'] = list(set(tag))
    dictionary['artist'] = list(set(artist))
    dictionary['group'] = list(set(group))
    return dictionary


def set_js_database():
    with open('data.js', 'w') as f:
        indexed_json = merge_json()
        unique_json = json.dumps(serialize_unique(indexed_json), separators=','':')
        indexed_json = json.dumps(indexed_json, separators=','':')
        f.write('var data = ' + indexed_json)
        f.write(';\nvar tags = ' + unique_json)
